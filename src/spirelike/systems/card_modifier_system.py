from __future__ import annotations

from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, CardModifierInstance


def modifier_id_of(modifier) -> str:
    if isinstance(modifier, CardModifierInstance):
        return modifier.modifier_id
    return str(modifier)


class CardModifierSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def active_modifiers(self, card: CardInstance) -> list[CardModifierInstance]:
        active: list[CardModifierInstance] = []
        normalized: list[CardModifierInstance] = []
        changed = False
        for modifier in card.modifiers:
            if isinstance(modifier, CardModifierInstance):
                instance = modifier
            else:
                modifier_id = str(modifier)
                modifier_def = self.registry.card_modifiers.get(modifier_id)
                if modifier_def is None:
                    continue
                data = modifier_def.data
                instance = CardModifierInstance(
                    modifier_id=modifier_id,
                    modifier_type=str(data.get("type", "enchantment")),
                    duration=str(data.get("duration", "run")),
                )
                changed = True
            if instance.modifier_id in self.registry.card_modifiers:
                normalized.append(instance)
                active.append(instance)
        if changed:
            card.modifiers = normalized
        return active

    def find_modifier(self, card: CardInstance, modifier_id: str) -> CardModifierInstance | None:
        for modifier in self.active_modifiers(card):
            if modifier.modifier_id == modifier_id:
                return modifier
        return None

    def can_apply(self, card: CardInstance, modifier_id: str) -> tuple[bool, str]:
        if modifier_id not in self.registry.card_modifiers:
            return False, "不明なModifierです"
        modifier_def = self.registry.card_modifier(modifier_id)
        card_def = self.registry.card(card.card_id)
        valid_targets = modifier_def.get("valid_targets", {}) or {}

        if valid_targets.get("card_types") and card_def.get("type") not in valid_targets["card_types"]:
            return False, "対象タイプが違います"
        if valid_targets.get("exclude_card_types") and card_def.get("type") in valid_targets["exclude_card_types"]:
            return False, "対象外タイプです"
        if valid_targets.get("rarities") and card_def.get("rarity") not in valid_targets["rarities"]:
            return False, "対象レアリティが違います"
        if valid_targets.get("exclude_rarities") and card_def.get("rarity") in valid_targets["exclude_rarities"]:
            return False, "対象外レアリティです"
        return True, ""

    def apply_modifier(
        self,
        card: CardInstance,
        modifier_id: str,
        *,
        duration_override: str | None = None,
        stacks: int = 1,
        source: str | None = None,
    ) -> bool:
        ok, _ = self.can_apply(card, modifier_id)
        if not ok:
            return False
        modifier_def = self.registry.card_modifier(modifier_id)
        stacking = str(modifier_def.get("stacking", "unique"))
        existing = self.find_modifier(card, modifier_id)
        stacks = max(1, int(stacks))

        if existing:
            if stacking == "stack":
                existing.stacks += stacks
                max_stacks = modifier_def.get("max_stacks")
                if max_stacks is not None:
                    existing.stacks = min(existing.stacks, int(max_stacks))
                return True
            if stacking == "replace":
                existing.stacks = stacks
                existing.duration = duration_override or str(modifier_def.get("duration", "run"))
                existing.source = source
                return True
            return False

        card.modifiers.append(
            CardModifierInstance(
                modifier_id=modifier_id,
                modifier_type=str(modifier_def.get("type", "enchantment")),
                duration=duration_override or str(modifier_def.get("duration", "run")),
                stacks=stacks,
                source=source,
            )
        )
        return True

    def remove_modifier(self, card: CardInstance, modifier_id: str, stacks: int | None = None) -> bool:
        modifier = self.find_modifier(card, modifier_id)
        if modifier is None:
            return False
        if stacks is not None and stacks > 0 and modifier.stacks > stacks:
            modifier.stacks -= int(stacks)
            return True
        card.modifiers = [m for m in self.active_modifiers(card) if m.instance_id != modifier.instance_id]
        return True

    def remove_by_type(self, card: CardInstance, modifier_type: str, count: int | None = None) -> int:
        removed = 0
        kept: list[CardModifierInstance] = []
        for modifier in self.active_modifiers(card):
            if modifier.modifier_type == modifier_type and (count is None or removed < count):
                removed += 1
                continue
            kept.append(modifier)
        card.modifiers = kept
        return removed

    def card_has_modifier(self, card: CardInstance, modifier_id: str) -> bool:
        return self.find_modifier(card, modifier_id) is not None

    def modify_card_cost(self, combat, card: CardInstance, base_cost: int) -> int:
        return max(0, self._apply_numeric_modifiers(combat, card, base_cost, "calculate_card_cost"))

    def modify_card_damage(self, combat, card: CardInstance, base_damage: int) -> int:
        return max(0, self._apply_numeric_modifiers(combat, card, base_damage, "calculate_card_damage"))

    def modify_card_block(self, combat, card: CardInstance, base_block: int) -> int:
        return max(0, self._apply_numeric_modifiers(combat, card, base_block, "calculate_card_block"))

    def _apply_numeric_modifiers(self, combat, card: CardInstance, base_value: int, event_name: str) -> int:
        current = int(base_value)
        for modifier in self.active_modifiers(card):
            modifier_def = self.registry.card_modifier(modifier.modifier_id)
            for rule in modifier_def.get("modifiers", []) or []:
                if rule.get("event") != event_name:
                    continue
                operation = str(rule.get("operation", "add"))
                value = self.resolve_modifier_value(rule.get("value", 0), combat, card, modifier)
                # stack=trueが明示されていない限り、数値modifierはスタック数ぶん効く。
                if rule.get("stack_multiplier", True):
                    value *= max(1, int(modifier.stacks))
                if operation == "add":
                    current += int(value)
                elif operation == "multiply":
                    current = int(current * float(value))
                elif operation == "set":
                    current = int(value)
                if "min" in rule:
                    current = max(int(rule["min"]), current)
                if "max" in rule:
                    current = min(int(rule["max"]), current)
        return current

    def resolve_modifier_value(self, value: Any, combat, card: CardInstance, modifier: CardModifierInstance):
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return 0
        if isinstance(value, dict):
            if value.get("type") == "modifier_stacks":
                return int(modifier.stacks)
            if value.get("type") == "status_stacks":
                target = combat.run_state.player if value.get("target", "player") == "player" else None
                return int(getattr(target, "statuses", {}).get(value.get("status"), 0))
        return 0

    def flag_added(self, card: CardInstance, flag: str) -> bool:
        for modifier in self.active_modifiers(card):
            modifier_def = self.registry.card_modifier(modifier.modifier_id)
            flags = modifier_def.get("flags", {}) or {}
            if flag in (flags.get("add", []) or []):
                return True
        return False

    def flag_removed(self, card: CardInstance, flag: str) -> bool:
        for modifier in self.active_modifiers(card):
            modifier_def = self.registry.card_modifier(modifier.modifier_id)
            flags = modifier_def.get("flags", {}) or {}
            if flag in (flags.get("remove", []) or []):
                return True
        return False

    def fire_card_modifier_event(self, combat, event_name: str, card: CardInstance, event_context: dict[str, Any]) -> None:
        for modifier in list(self.active_modifiers(card)):
            modifier_def = self.registry.card_modifier(modifier.modifier_id)
            for trigger in modifier_def.get("triggers", []) or []:
                if trigger.get("event") != event_name:
                    continue
                context = {
                    **event_context,
                    "source": combat.run_state.player,
                    "target": combat.run_state.player,
                    "card": card,
                    "card_def": combat.registry.card(card.card_id),
                    "modifier": modifier,
                }
                combat.executor.execute_many(trigger.get("effects", []), context)
                if combat.state.pending_selection is not None:
                    return

    def cleanup_combat_modifiers(self, run_state) -> None:
        for card in run_state.player.deck:
            card.modifiers = [m for m in self.active_modifiers(card) if m.duration != "combat"]
