from __future__ import annotations

from typing import Any

from spirelike.systems.actions import (
    AddCardToPileAction,
    ApplyStatusAction,
    DamageAction,
    DrawCardsAction,
    GainBlockAction,
    GainEnergyAction,
    HealAction,
)


class EffectExecutor:
    def __init__(self, combat: "CombatSystem") -> None:
        self.combat = combat

    def execute_many(self, effects: list[dict[str, Any]], context: dict[str, Any]) -> None:
        for effect in effects or []:
            self.execute(effect, context)
            if self.combat.state.outcome == "defeat":
                break

    def execute(self, effect: dict[str, Any], context: dict[str, Any]) -> None:
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
        elif effect_type == "add_card_to_draw_pile":
            self._add_card_to_pile(effect, context, "draw")
        elif effect_type == "add_card_to_hand":
            self._add_card_to_pile(effect, context, "hand")
        elif effect_type == "repeat":
            times = self.resolve_amount(effect.get("times", 1), context)
            for _ in range(max(0, times)):
                self.execute_many(effect.get("effects", []), context)
        elif effect_type == "if":
            branch = effect.get("then", []) if self._check_condition(effect.get("condition", {}), context) else effect.get("else", [])
            self.execute_many(branch, context)
        elif effect_type in (None, "none"):
            return
        else:
            self.combat.log(f"未実装効果: {effect_type}")

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
                )
            )

    def _gain_block(self, effect: dict[str, Any], context: dict[str, Any]) -> None:
        amount = self.resolve_amount(effect.get("amount", 0), context)
        targets = self.resolve_targets(effect.get("target", "self"), context)
        for target in targets:
            self.combat.enqueue_action(GainBlockAction(target=target, amount=amount))

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
