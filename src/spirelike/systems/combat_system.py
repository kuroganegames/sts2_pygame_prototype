from __future__ import annotations

import random
from typing import Any, Optional

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, CombatState, EnemyInstance, PlayerState, RunState
from spirelike.systems.effect_executor import EffectExecutor


DURATION_STATUSES = {"weak", "vulnerable"}


class CombatSystem:
    def __init__(
        self,
        registry: ContentRegistry,
        run_state: RunState,
        enemy_ids: list[str],
        rng: random.Random,
    ) -> None:
        self.registry = registry
        self.run_state = run_state
        self.rng = rng
        enemies = [self._create_enemy(enemy_id) for enemy_id in enemy_ids]
        draw_pile = [card.clone_for_combat() for card in run_state.player.deck]
        rng.shuffle(draw_pile)
        self.state = CombatState(
            run_state=run_state,
            enemies=enemies,
            draw_pile=draw_pile,
            hand=[],
            discard_pile=[],
            exhaust_pile=[],
            energy=run_state.player.base_energy,
        )
        self.executor = EffectExecutor(self)
        self.choose_enemy_moves()
        self.fire_relic_event("combat_start")
        self.start_player_turn(first_turn=True)

    def _create_enemy(self, enemy_id: str) -> EnemyInstance:
        enemy_def = self.registry.enemy(enemy_id)
        hp_def = enemy_def.get("hp", {}) or {}
        hp = self.rng.randint(int(hp_def.get("min", 10)), int(hp_def.get("max", 10)))
        return EnemyInstance(
            enemy_id=enemy_id,
            name=str(enemy_def.get("name", enemy_id)),
            hp=hp,
            max_hp=hp,
            block=int(enemy_def.get("block", 0)),
        )

    def log(self, text: str) -> None:
        self.state.add_log(text)

    def start_player_turn(self, first_turn: bool = False) -> None:
        if self.state.outcome is not None:
            return
        player = self.run_state.player
        self.state.turn_number += 1
        player.block = 0
        self.state.energy = player.base_energy
        self.fire_relic_event("turn_start")
        self.draw_cards(5)
        self.log(f"ターン {self.state.turn_number} 開始")

    def draw_cards(self, amount: int) -> None:
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

    def add_to_hand(self, card: CardInstance) -> None:
        if len(self.state.hand) < 10:
            self.state.hand.append(card)
        else:
            self.state.discard_pile.append(card)

    def can_play(self, card: CardInstance) -> tuple[bool, str]:
        cost = self.get_card_cost(card)
        if isinstance(cost, str) and cost.upper() == "X":
            return True, ""
        if int(cost) > self.state.energy:
            return False, "エナジー不足"
        return True, ""

    def get_card_cost(self, card: CardInstance):
        return self.registry.card_cost(card.card_id, card.upgraded)

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
        self.state.energy -= spent
        self.state.hand.remove(card)

        self.log(f"{self.registry.card_display_name(card.card_id, card.upgraded)} を使用")
        effects = self.registry.card_effects(card.card_id, card.upgraded)
        context = {
            "source": self.run_state.player,
            "target": target,
            "card": card,
            "card_def": card_def,
            "spent_energy": spent,
        }
        self.executor.execute_many(effects, context)
        # Powerの常駐処理は今後の拡張ポイント。現時点では使用後捨て札へ。
        if not card.temporary:
            self.state.discard_pile.append(card)
        else:
            self.state.exhaust_pile.append(card)
        self._remove_dead_enemies()
        self._check_victory_or_defeat()
        return True

    def end_player_turn(self) -> None:
        if self.state.outcome is not None:
            return
        self.state.discard_pile.extend(self.state.hand)
        self.state.hand.clear()
        self._tick_statuses(self.run_state.player, owner="player")

        for enemy in self.state.alive_enemies():
            enemy.block = 0
        for enemy in list(self.state.alive_enemies()):
            self._enemy_take_turn(enemy)
            self._check_victory_or_defeat()
            if self.state.outcome is not None:
                return

        for enemy in self.state.alive_enemies():
            self._tick_statuses(enemy, owner="enemy")
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

    def deal_damage(self, source, target, amount: int, card_def: Optional[dict[str, Any]] = None) -> int:
        if target is None or amount <= 0:
            return 0
        amount = self._calculate_damage(source, target, amount, card_def or {})
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

    def _calculate_damage(self, source, target, amount: int, card_def: dict[str, Any]) -> int:
        result = int(amount)
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
        # 毒はターン終了時にダメージを与えて1減る。
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
                self.log(f"{enemy.name}を倒した")
                enemy.next_move = None

    def _check_victory_or_defeat(self) -> None:
        if not self.run_state.player.is_alive():
            self.state.outcome = "defeat"
            self.log("敗北")
        elif not self.state.alive_enemies():
            self.state.outcome = "victory"
            self.fire_relic_event("combat_end")
            self.log("勝利")

    def fire_relic_event(self, event_name: str) -> None:
        player = self.run_state.player
        for relic in player.relics:
            relic_def = self.registry.relic(relic.relic_id)
            for trigger in relic_def.get("triggers", []) or []:
                if trigger.get("event") != event_name:
                    continue
                context = {"source": player, "target": player, "relic": relic, "card_def": {}}
                self.executor.execute_many(trigger.get("effects", []), context)
