from __future__ import annotations

from typing import Any

from spirelike.models.selection import CardSelectionRequest, CardSelectionResult
from spirelike.systems.actions import (
    AddCardToPileAction,
    ApplyStatusAction,
    DamageAction,
    DrawCardsAction,
    GainBlockAction,
    GainEnergyAction,
    HealAction,
    LoseHpAction,
    RequestCardSelectionAction,
)
from spirelike.systems.card_operation_system import CardOperationSystem
from spirelike.systems.card_selection_system import CardSelectionSystem


SELECTION_EFFECTS = {
    "upgrade_card": "upgrade",
    "remove_card_from_deck": "remove",
    "transform_card": "transform",
    "exhaust_cards": "exhaust",
    "discard_cards": "discard",
    "fetch_card_to_hand": "fetch_to_hand",
    "apply_card_modifier": "apply_modifier",
    "remove_card_modifier": "remove_modifier",
    "cleanse_card_modifiers": "cleanse_modifiers",
}


class EffectExecutor:
    def __init__(self, combat: "CombatSystem") -> None:
        self.combat = combat

    def execute_many(self, effects: list[dict[str, Any]], context: dict[str, Any]) -> None:
        effects = effects or []
        for index, effect in enumerate(effects):
            self.execute(effect, context, remaining_effects=effects[index + 1 :])
            if self.combat.state.outcome == "defeat" or self.combat.state.pending_selection is not None:
                break

    def execute(
        self,
        effect: dict[str, Any],
        context: dict[str, Any],
        remaining_effects: list[dict[str, Any]] | None = None,
    ) -> None:
        effect_type = effect.get("type")
        if effect_type == "damage":
            self._damage(effect, context)
        elif effect_type == "gain_block":
            self._gain_block(effect, context)
        elif effect_type == "draw_cards":
            amount = self.resolve_amount(effect.get("amount", 1), context)
            self.combat.enqueue_action(DrawCardsAction(amount))
        elif effect_type == "gain_energy":
            amount = self.resolve_amount(effect.get("amount", 1), context)
            self.combat.enqueue_action(GainEnergyAction(amount))
        elif effect_type == "apply_status":
            self._apply_status(effect, context)
        elif effect_type == "heal":
            amount = self.resolve_amount(effect.get("amount", 0), context)
            self.combat.enqueue_action(HealAction(amount))
        elif effect_type == "lose_hp":
            amount = self.resolve_amount(effect.get("amount", 0), context)
            targets = self.resolve_targets(effect.get("target", "player"), context)
            for target in targets:
                self.combat.enqueue_action(LoseHpAction(target=target, amount=amount))
        elif effect_type == "add_card_to_draw_pile":
            self._add_card_to_pile(effect, context, "draw")
        elif effect_type == "add_card_to_hand":
            self._add_card_to_pile(effect, context, "hand")
        elif effect_type in SELECTION_EFFECTS:
            self._selection_operation(effect, context, SELECTION_EFFECTS[effect_type], remaining_effects or [])
        elif effect_type == "repeat":
            times = self.resolve_amount(effect.get("times", 1), context)
            for _ in range(max(0, times)):
                self.execute_many(effect.get("effects", []), context)
                if self.combat.state.pending_selection is not None:
                    break
        elif effect_type == "if":
            branch = effect.get("then", []) if self._check_condition(effect.get("condition", {}), context) else effect.get("else", [])
            self.execute_many(branch, context)
        elif effect_type in (None, "none"):
            return
        else:
            self.combat.log(f"未実装効果: {effect_type}")

    def _selection_operation(
        self,
        effect: dict[str, Any],
        context: dict[str, Any],
        operation_type: str,
        remaining_effects: list[dict[str, Any]],
    ) -> None:
        selector = effect.get("selector", {}) or {}
        zones = selector.get("zones") or selector.get("zone") or ["master_deck"]
        if isinstance(zones, str):
            zones = [zones]
        count = int(selector.get("count", effect.get("count", 1)))
        allow_skip = bool(selector.get("allow_skip", effect.get("allow_skip", False)))
        operation = {
            "type": operation_type,
            **{k: v for k, v in effect.items() if k not in {"type", "selector", "title", "message"}},
        }
        request = CardSelectionRequest(
            title=str(effect.get("title", self._default_title(operation_type))),
            message=str(effect.get("message", self._default_message(operation_type))),
            source_zones=list(zones),
            exact_count=count,
            min_count=count,
            max_count=count,
            allow_skip=allow_skip,
            filter=selector.get("filter", {}) or {},
            operation=operation,
            context={"effect_context": context, "remaining_effects": list(remaining_effects or [])},
        )

        if selector.get("player_choice", False):
            self.combat.enqueue_action(RequestCardSelectionAction(request))
            return

        candidates = CardSelectionSystem(self.combat.registry).collect_candidates(
            self.combat.run_state,
            request,
            self.combat.state,
        )
        if not candidates:
            return
        mode = selector.get("mode", "random")
        if mode == "all":
            selected = candidates[:count] if count else candidates
        else:
            selected = self.combat.rng.sample(candidates, k=min(count, len(candidates)))
        result = CardSelectionResult(
            request_id=request.request_id,
            selected_instance_ids=[candidate.card.instance_id for candidate in selected],
        )
        CardOperationSystem(self.combat.registry, self.combat.rng).apply_result(
            self.combat.run_state,
            request,
            result,
            combat=self.combat,
        )

    def _default_title(self, operation_type: str) -> str:
        return {
            "upgrade": "カード強化",
            "remove": "カード削除",
            "transform": "カード変化",
            "exhaust": "カード廃棄",
            "discard": "カード破棄",
            "fetch_to_hand": "カード回収",
            "apply_modifier": "カード修飾",
            "remove_modifier": "修飾解除",
            "cleanse_modifiers": "修飾浄化",
        }.get(operation_type, "カード選択")

    def _default_message(self, operation_type: str) -> str:
        return {
            "upgrade": "強化するカードを選んでください。",
            "remove": "削除するカードを選んでください。",
            "transform": "変化させるカードを選んでください。",
            "exhaust": "廃棄するカードを選んでください。",
            "discard": "捨てるカードを選んでください。",
            "fetch_to_hand": "手札に加えるカードを選んでください。",
            "apply_modifier": "修飾するカードを選んでください。",
            "remove_modifier": "修飾を解除するカードを選んでください。",
            "cleanse_modifiers": "浄化するカードを選んでください。",
        }.get(operation_type, "カードを選んでください。")

    def _damage(self, effect: dict[str, Any], context: dict[str, Any]) -> None:
        amount = self.resolve_amount(effect.get("amount", 0), context)
        targets = self.resolve_targets(effect.get("target", "selected_enemy"), context)
        for target in targets:
            self.combat.enqueue_action(
                DamageAction(
                    source=context.get("source"),
                    target=target,
                    amount=amount,
                    card_def=context.get("card_def", {}),
                    card=context.get("card"),
                )
            )

    def _gain_block(self, effect: dict[str, Any], context: dict[str, Any]) -> None:
        amount = self.resolve_amount(effect.get("amount", 0), context)
        targets = self.resolve_targets(effect.get("target", "self"), context)
        for target in targets:
            self.combat.enqueue_action(GainBlockAction(target=target, amount=amount, card=context.get("card")))

    def _apply_status(self, effect: dict[str, Any], context: dict[str, Any]) -> None:
        status_id = effect.get("status")
        stacks = self.resolve_amount(effect.get("stacks", 1), context)
        targets = self.resolve_targets(effect.get("target", "selected_enemy"), context)
        for target in targets:
            self.combat.enqueue_action(ApplyStatusAction(target=target, status_id=str(status_id), stacks=stacks))

    def _add_card_to_pile(self, effect: dict[str, Any], context: dict[str, Any], pile: str) -> None:
        card_id = str(effect.get("card"))
        amount = self.resolve_amount(effect.get("amount", 1), context)
        self.combat.enqueue_action(AddCardToPileAction(card_id=card_id, amount=amount, pile=pile))

    def resolve_targets(self, target_spec: str, context: dict[str, Any]) -> list[Any]:
        player = self.combat.state.run_state.player
        if target_spec in {"self", "source"}:
            return [context.get("source")]
        if target_spec in {"player", "target_player"}:
            return [player]
        if target_spec in {"selected_enemy", "target"}:
            target = context.get("target")
            return [target] if target is not None and getattr(target, "is_alive", lambda: True)() else []
        if target_spec == "all_enemies":
            return self.combat.state.alive_enemies()
        if target_spec == "random_enemy":
            enemies = self.combat.state.alive_enemies()
            return [self.combat.rng.choice(enemies)] if enemies else []
        return []

    def resolve_amount(self, value: Any, context: dict[str, Any]) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            if value.upper() == "X":
                return int(context.get("spent_energy", 0))
            try:
                return int(value)
            except ValueError:
                return 0
        if isinstance(value, dict):
            if "base" in value:
                result = self.resolve_amount(value.get("base", 0), context)
                for add in value.get("plus", []) or []:
                    result += self.resolve_amount(add, context)
                return result
            value_type = value.get("type")
            if value_type == "status_stacks":
                target = self._amount_target(value, context)
                return int(getattr(target, "statuses", {}).get(value.get("status"), 0))
            if value_type == "power_stacks":
                power_id = value.get("power")
                if power_id:
                    return self.combat.power_system.power_stacks(self.combat, str(power_id))
                power = context.get("power")
                return int(getattr(power, "stacks", 0))
            if value_type == "modifier_stacks":
                modifier = context.get("modifier")
                return int(getattr(modifier, "stacks", 0))
            if value_type == "percent_max_hp":
                percent = float(value.get("percent", 0))
                return int(self.combat.state.run_state.player.max_hp * percent / 100)
            if value_type == "spent_energy":
                return int(context.get("spent_energy", 0))
        return 0

    def _amount_target(self, spec: dict[str, Any], context: dict[str, Any]):
        target_key = spec.get("target", "self")
        if target_key == "selected_enemy":
            return context.get("target")
        if target_key == "player":
            return self.combat.state.run_state.player
        return context.get("source")

    def _check_condition(self, condition: dict[str, Any], context: dict[str, Any]) -> bool:
        condition_type = condition.get("type")
        if condition_type == "target_has_status":
            targets = self.resolve_targets(condition.get("target", "selected_enemy"), context)
            status = condition.get("status")
            required = int(condition.get("stacks_at_least", 1))
            return any(getattr(target, "statuses", {}).get(status, 0) >= required for target in targets)
        if condition_type == "player_hp_below_percent":
            player = self.combat.state.run_state.player
            percent = float(condition.get("percent", 50))
            return player.hp <= player.max_hp * percent / 100
        return False
