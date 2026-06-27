from __future__ import annotations

import random
from typing import Any, Optional

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, CombatState, EnemyInstance, PlayerState, RunState
from spirelike.models.selection import CardSelectionResult
from spirelike.profile.run_metrics import RunMetricsSystem
from spirelike.save.combat_serializer import combat_snapshot_from_dict, combat_snapshot_to_dict
from spirelike.systems.action_queue import ActionQueue
from spirelike.systems.actions import (
    DrawCardsAction,
    EndTurnHandCleanupAction,
    FinishCardUseAction,
    PlayCardAction,
    TriggerEventAction,
)
from spirelike.systems.ancient_system import AncientSystem
from spirelike.systems.card_modifier_system import CardModifierSystem
from spirelike.systems.card_operation_system import CardOperationSystem
from spirelike.systems.card_rules import CardRules
from spirelike.systems.effect_executor import EffectExecutor
from spirelike.systems.power_system import PowerSystem
from spirelike.systems.run_modifier_system import RunModifierSystem


DURATION_STATUSES = {"weak", "vulnerable"}


class CombatSystem:
    def __init__(
        self,
        registry: ContentRegistry,
        run_state: RunState,
        enemy_ids: list[str],
        rng: random.Random,
        snapshot: dict[str, Any] | None = None,
    ) -> None:
        self.registry = registry
        self.run_state = run_state
        self.rng = rng
        self.card_modifier_system = CardModifierSystem(registry)
        self.card_rules = CardRules(registry)
        self.power_system = PowerSystem(registry)
        self.card_operation_system = CardOperationSystem(registry, rng)
        self.run_modifier_system = RunModifierSystem(registry)
        self.action_queue = ActionQueue()
        self.draw_per_turn = 5
        self.executor = EffectExecutor(self)

        if snapshot is not None:
            self._restore_from_snapshot(snapshot)
            return

        enemies = [self._create_enemy(enemy_id) for enemy_id in enemy_ids]
        draw_pile = self._build_combat_draw_pile()
        self.state = CombatState(
            run_state=run_state,
            enemies=enemies,
            draw_pile=draw_pile,
            hand=[],
            discard_pile=[],
            exhaust_pile=[],
            limbo=[],
            powers=[],
            energy=run_state.player.base_energy,
        )
        self.choose_enemy_moves()
        self.enqueue_action(TriggerEventAction("combat_start", {"owner": "player"}))
        self.resolve_actions()
        self.start_player_turn(first_turn=True)

    def _restore_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        self.state, restored_rng = combat_snapshot_from_dict(snapshot, self.run_state)
        self.rng = restored_rng
        self.card_operation_system = CardOperationSystem(self.registry, self.rng)
        self.state.pending_selection = None
        self.log("戦闘を再開")

    def to_snapshot(self) -> dict[str, Any]:
        return combat_snapshot_to_dict(self)

    def can_save_combat(self) -> tuple[bool, str]:
        if self.state.outcome is not None:
            return False, "戦闘終了処理中です"
        if self.state.pending_selection is not None:
            return False, "カード選択中は保存できません"
        if self.action_queue.is_resolving:
            return False, "効果解決中は保存できません"
        if self.action_queue.has_pending():
            return False, "未解決Actionがあります"
        if self.state.limbo:
            return False, "カード解決中は保存できません"
        return True, ""

    def _build_combat_draw_pile(self) -> list[CardInstance]:
        cards = [card.clone_for_combat() for card in self.run_state.player.deck]
        innate_cards = [card for card in cards if self.card_rules.has_flag(card, "innate")]
        regular_cards = [card for card in cards if not self.card_rules.has_flag(card, "innate")]
        self.rng.shuffle(regular_cards)
        self.rng.shuffle(innate_cards)
        return regular_cards + innate_cards

    def _create_enemy(self, enemy_id: str) -> EnemyInstance:
        enemy_def = self.registry.enemy(enemy_id)
        hp_def = enemy_def.get("hp", {}) or {}
        hp = self.rng.randint(int(hp_def.get("min", 10)), int(hp_def.get("max", 10)))
        hp_multiplier = self.run_modifier_system.enemy_hp_multiplier(self.run_state)
        hp = max(1, int(hp * hp_multiplier))
        RunMetricsSystem.record_enemy_seen(self.run_state, enemy_id)
        return EnemyInstance(
            enemy_id=enemy_id,
            name=str(enemy_def.get("name", enemy_id)),
            hp=hp,
            max_hp=hp,
            block=int(enemy_def.get("block", 0)),
        )

    def enqueue_action(self, action) -> None:
        self.action_queue.add(action)

    def resolve_actions(self) -> None:
        self.action_queue.resolve_all(self)

    def log(self, text: str) -> None:
        self.state.add_log(text)

    def start_player_turn(self, first_turn: bool = False) -> None:
        if self.state.outcome is not None:
            return
        player = self.run_state.player
        self.state.turn_number += 1
        self.state.cards_played_this_turn = 0
        player.block = 0
        self.state.energy = player.base_energy
        self.enqueue_action(TriggerEventAction("turn_start", {"owner": "player"}))
        self.enqueue_action(DrawCardsAction(self.draw_per_turn))
        self.resolve_actions()
        self.log(f"ターン {self.state.turn_number} 開始")

    def draw_cards(self, amount: int) -> None:
        self.enqueue_action(DrawCardsAction(amount))
        if not self.action_queue.is_resolving:
            self.resolve_actions()

    def draw_cards_immediate(self, amount: int) -> None:
        for _ in range(max(0, amount)):
            if len(self.state.hand) >= 10:
                return
            if not self.state.draw_pile:
                if not self.state.discard_pile:
                    return
                self.state.draw_pile = self.state.discard_pile
                self.state.discard_pile = []
                self.rng.shuffle(self.state.draw_pile)
                self.log("捨て札をシャッフル")
            card = self.state.draw_pile.pop()
            self.add_to_hand(card)
            RunMetricsSystem.record_card_seen(self.run_state, card.card_id)
            context = {
                "source": self.run_state.player,
                "target": self.run_state.player,
                "card": card,
                "card_def": self.registry.card(card.card_id),
            }
            self.enqueue_action(TriggerEventAction("card_drawn", context))

    def add_to_hand(self, card: CardInstance) -> None:
        if len(self.state.hand) < 10:
            self.state.hand.append(card)
        else:
            self.state.discard_pile.append(card)

    def add_generated_card_to_pile(self, card_id: str, amount: int, pile: str) -> None:
        for _ in range(max(0, amount)):
            card = CardInstance(card_id=card_id, temporary=True)
            if pile == "hand":
                self.add_to_hand(card)
            elif pile == "discard":
                self.state.discard_pile.append(card)
            elif pile == "exhaust":
                self.state.exhaust_pile.append(card)
            else:
                self.state.draw_pile.append(card)
        self.log(f"{card_id} を{amount}枚追加")

    def can_play(self, card: CardInstance) -> tuple[bool, str]:
        if self.state.pending_selection is not None:
            return False, "カード選択中"
        if self.card_rules.has_flag(card, "unplayable"):
            return False, "使用不可"
        cost = self.get_card_cost(card)
        if isinstance(cost, str) and cost.upper() == "X":
            return True, ""
        try:
            numeric_cost = int(cost)
        except (TypeError, ValueError):
            return False, "不正なコスト"
        if numeric_cost > self.state.energy:
            return False, "エナジー不足"
        return True, ""

    def get_card_cost(self, card: CardInstance):
        if "cost" in card.state:
            base_cost = card.state["cost"]
        else:
            base_cost = self.registry.card_cost(card.card_id, card.upgraded)
        if isinstance(base_cost, str):
            return base_cost
        return self.card_modifier_system.modify_card_cost(self, card, int(base_cost))

    def play_card(self, card: CardInstance, target: Optional[EnemyInstance] = None) -> bool:
        if card not in self.state.hand or self.state.outcome is not None:
            return False
        ok, reason = self.can_play(card)
        if not ok:
            self.log(reason)
            return False
        card_def = self.registry.card(card.card_id)
        target_rule = card_def.get("target", "none")
        if target_rule == "enemy" and target is None:
            self.log("対象を選んでください")
            return False

        cost = self.get_card_cost(card)
        spent = self.state.energy if isinstance(cost, str) and cost.upper() == "X" else int(cost)
        self.enqueue_action(PlayCardAction(card=card, target=target, spent_energy=spent))
        self.resolve_actions()
        return True

    def resolve_card_play_immediate(
        self,
        card: CardInstance,
        target: Optional[EnemyInstance],
        spent_energy: int,
    ) -> None:
        if card not in self.state.hand:
            return
        card_def = self.registry.card(card.card_id)
        self.state.energy -= spent_energy
        self.move_card(card, "hand", "limbo")
        self.state.cards_played_this_turn += 1
        RunMetricsSystem.record_card_played(self.run_state, card.card_id)

        context = {
            "source": self.run_state.player,
            "target": target,
            "card": card,
            "card_def": card_def,
            "spent_energy": spent_energy,
        }

        self.log(f"{self.registry.card_display_name(card.card_id, card.upgraded)} を使用")
        self.enqueue_action(TriggerEventAction("card_played", context))
        self.executor.execute_many(self.registry.card_effects(card.card_id, card.upgraded), context)
        if self.state.pending_selection is None:
            self.enqueue_action(TriggerEventAction("card_resolved", context))
            self.enqueue_action(FinishCardUseAction(card=card, context=context))

    def complete_card_selection(self, result: CardSelectionResult) -> None:
        request = self.state.pending_selection
        if request is None:
            return
        self.state.pending_selection = None
        self.card_operation_system.apply_result(self.run_state, request, result, combat=self)

        effect_context = request.context.get("effect_context", {}) if request.context else {}
        remaining_effects = request.context.get("remaining_effects", []) if request.context else []
        if remaining_effects and self.state.pending_selection is None:
            self.executor.execute_many(remaining_effects, effect_context)

        card = effect_context.get("card") if isinstance(effect_context, dict) else None
        if self.state.pending_selection is None and card is not None and card in self.state.limbo:
            self.enqueue_action(TriggerEventAction("card_resolved", effect_context))
            self.enqueue_action(FinishCardUseAction(card=card, context=effect_context))
        self.resolve_actions()

    def move_card(self, card: CardInstance, from_zone: str, to_zone: str) -> bool:
        source = getattr(self.state, from_zone)
        destination = getattr(self.state, to_zone)
        if card not in source:
            return False
        source.remove(card)
        destination.append(card)
        return True

    def remove_from_limbo(self, card: CardInstance) -> bool:
        if card not in self.state.limbo:
            return False
        self.state.limbo.remove(card)
        return True

    def end_player_turn(self) -> None:
        if self.state.outcome is not None or self.state.pending_selection is not None:
            return
        self.enqueue_action(TriggerEventAction("player_turn_end", {"owner": "player"}))
        self.enqueue_action(EndTurnHandCleanupAction())
        self.resolve_actions()
        self._tick_statuses(self.run_state.player, owner="player")

        for enemy in self.state.alive_enemies():
            enemy.block = 0
        self.enqueue_action(TriggerEventAction("enemy_turn_start", {"owner": "enemy"}))
        self.resolve_actions()
        for enemy in list(self.state.alive_enemies()):
            self._enemy_take_turn(enemy)
            self._check_victory_or_defeat()
            if self.state.outcome is not None:
                return

        for enemy in self.state.alive_enemies():
            self._tick_statuses(enemy, owner="enemy")
        self.enqueue_action(TriggerEventAction("enemy_turn_end", {"owner": "enemy"}))
        self.resolve_actions()
        self.choose_enemy_moves()
        self.start_player_turn()

    def _enemy_take_turn(self, enemy: EnemyInstance) -> None:
        move_id = enemy.next_move
        if not move_id:
            return
        enemy_def = self.registry.enemy(enemy.enemy_id)
        move = (enemy_def.get("moves", {}) or {}).get(move_id, {})
        self.log(f"{enemy.name}: {move.get('name', move_id)}")
        context = {"source": enemy, "target": self.run_state.player, "card_def": {"type": "attack"}}
        self.executor.execute_many(move.get("effects", []), context)
        self.resolve_actions()
        enemy.last_move = move_id

    def choose_enemy_moves(self) -> None:
        for enemy in self.state.alive_enemies():
            enemy.next_move = self._choose_enemy_move(enemy)

    def _choose_enemy_move(self, enemy: EnemyInstance) -> str:
        enemy_def = self.registry.enemy(enemy.enemy_id)
        moves = enemy_def.get("moves", {}) or {}
        ai = enemy_def.get("ai", {}) or {}
        ai_type = ai.get("type", "weighted_random")
        if not moves:
            return ""
        if ai_type == "pattern":
            pattern = ai.get("pattern", list(moves.keys())) or list(moves.keys())
            move_id = pattern[enemy.move_index % len(pattern)]
            enemy.move_index += 1
            return move_id
        candidates = []
        for move_id, move in moves.items():
            if ai.get("avoid_same_move_twice") and enemy.last_move == move_id and len(moves) > 1:
                continue
            weight = float(move.get("weight", 1))
            if weight > 0:
                candidates.append((move_id, weight))
        if not candidates:
            candidates = [(move_id, 1.0) for move_id in moves]
        total = sum(weight for _, weight in candidates)
        roll = self.rng.uniform(0, total)
        upto = 0.0
        for move_id, weight in candidates:
            upto += weight
            if roll <= upto:
                return move_id
        return candidates[-1][0]

    def deal_damage(
        self,
        source,
        target,
        amount: int,
        card_def: Optional[dict[str, Any]] = None,
        card: CardInstance | None = None,
    ) -> int:
        if target is None or amount <= 0:
            return 0
        if hasattr(target, "is_alive") and not target.is_alive():
            return 0
        amount = self._calculate_damage(source, target, amount, card_def or {}, card)
        blocked = min(getattr(target, "block", 0), amount)
        target.block = max(0, getattr(target, "block", 0) - blocked)
        actual = amount - blocked
        if isinstance(target, PlayerState):
            target.lose_hp(actual)
            self.log(f"プレイヤーに{actual}ダメージ")
        else:
            target.hp = max(0, target.hp - actual)
            self.log(f"{target.name}に{actual}ダメージ")
        return actual

    def _calculate_damage(self, source, target, amount: int, card_def: dict[str, Any], card: CardInstance | None = None) -> int:
        result = int(amount)
        if card is not None:
            result = self.card_modifier_system.modify_card_damage(self, card, result)
        source_statuses = getattr(source, "statuses", {})
        target_statuses = getattr(target, "statuses", {})
        if card_def.get("type") == "attack":
            result += int(source_statuses.get("strength", 0))
        if source_statuses.get("weak", 0) > 0:
            result = int(result * 0.75)
        if target_statuses.get("vulnerable", 0) > 0:
            result = int(result * 1.5)
        return max(0, result)

    def apply_status(self, target, status_id: str, stacks: int) -> None:
        if target is None or stacks <= 0:
            return
        target.statuses[status_id] = int(target.statuses.get(status_id, 0)) + int(stacks)
        name = getattr(target, "name", "プレイヤー")
        status_name = self.registry.statuses.get(status_id).data.get("name", status_id) if status_id in self.registry.statuses else status_id
        self.log(f"{name}: {status_name} +{stacks}")

    def _tick_statuses(self, target, owner: str) -> None:
        poison = int(target.statuses.get("poison", 0))
        if poison > 0:
            self.deal_damage(target, target, poison, {"type": "status"})
            target.statuses["poison"] = max(0, poison - 1)
        for status_id in list(target.statuses.keys()):
            if status_id in DURATION_STATUSES:
                target.statuses[status_id] = max(0, int(target.statuses[status_id]) - 1)
            if target.statuses.get(status_id, 0) <= 0:
                target.statuses.pop(status_id, None)

    def _remove_dead_enemies(self) -> None:
        for enemy in self.state.enemies:
            if enemy.hp <= 0 and enemy.next_move is not None:
                RunMetricsSystem.record_enemy_defeated(self.run_state, enemy.enemy_id)
                self.log(f"{enemy.name}を倒した")
                enemy.next_move = None

    def _check_victory_or_defeat(self) -> None:
        if not self.run_state.player.is_alive():
            self.state.outcome = "defeat"
            self.log("敗北")
        elif not self.state.alive_enemies():
            if not self.state.combat_end_fired:
                self.state.combat_end_fired = True
                self.enqueue_action(TriggerEventAction("combat_end", {"owner": "player"}))
                self.card_modifier_system.cleanup_combat_modifiers(self.run_state)
            if self.state.outcome != "victory":
                self.state.outcome = "victory"
                self.log("勝利")

    def trigger_matches(self, when: dict[str, Any] | None, context: dict[str, Any]) -> bool:
        if not when:
            return True
        card_def = context.get("card_def") or {}
        card = context.get("card")

        if "card_type" in when and card_def.get("type") != when["card_type"]:
            return False
        if "card_rarity" in when and card_def.get("rarity") != when["card_rarity"]:
            return False
        if "card_has_tag" in when:
            tags = set(card_def.get("tags", []) or [])
            if when["card_has_tag"] not in tags:
                return False
        if "card_cost_at_least" in when and card is not None:
            cost = self.get_card_cost(card)
            if isinstance(cost, str):
                return False
            if int(cost) < int(when["card_cost_at_least"]):
                return False
        return True

    def fire_trigger_event(self, event_name: str, event_context: dict[str, Any] | None = None) -> None:
        event_context = event_context or {}
        player = self.run_state.player
        for relic in player.relics:
            relic_def = self.registry.relic(relic.relic_id)
            for trigger in relic_def.get("triggers", []) or []:
                if trigger.get("event") != event_name:
                    continue
                if not self.trigger_matches(trigger.get("when"), event_context):
                    continue
                context = {**event_context, "source": player, "target": player, "relic": relic, "card_def": event_context.get("card_def", {})}
                self.executor.execute_many(trigger.get("effects", []), context)
                if self.state.pending_selection is not None:
                    return

        ancient_system = AncientSystem(self.registry)
        for blessing in self.run_state.ancient_blessings:
            if blessing.ancient_id not in self.registry.ancients:
                continue
            ancient_def = self.registry.ancient(blessing.ancient_id)
            choice = ancient_system.find_choice(ancient_def, blessing.choice_id)
            if not choice:
                continue
            for trigger in choice.get("triggers", []) or []:
                if trigger.get("event") != event_name:
                    continue
                if not self.trigger_matches(trigger.get("when"), event_context):
                    continue
                context = {
                    **event_context,
                    "source": player,
                    "target": player,
                    "ancient_blessing": blessing,
                    "card_def": event_context.get("card_def", {}),
                }
                self.executor.execute_many(trigger.get("effects", []), context)
                if self.state.pending_selection is not None:
                    return

        for power in list(self.state.powers):
            if power.owner != "player":
                continue
            power_def = self.power_system.power_def(power)
            for trigger in power_def.get("triggers", []) or []:
                if trigger.get("event") != event_name:
                    continue
                if not self.trigger_matches(trigger.get("when"), event_context):
                    continue
                context = {
                    **event_context,
                    "source": player,
                    "target": player,
                    "power": power,
                    "card_def": event_context.get("card_def", {}),
                }
                self.executor.execute_many(trigger.get("effects", []), context)
                if self.state.pending_selection is not None:
                    return

        card = event_context.get("card")
        if card is not None:
            self.card_modifier_system.fire_card_modifier_event(self, event_name, card, event_context)
            if self.state.pending_selection is not None:
                return

        if not self.action_queue.is_resolving:
            self.resolve_actions()

    def fire_relic_event(self, event_name: str) -> None:
        self.fire_trigger_event(event_name)
