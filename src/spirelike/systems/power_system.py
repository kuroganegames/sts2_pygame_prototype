from __future__ import annotations

from copy import deepcopy
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, PowerInstance


class PowerSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def add_power_from_card(self, combat: "CombatSystem", card: CardInstance) -> PowerInstance:
        power_def = self.power_def_for_card(card.card_id, card.upgraded)
        card_def = self.registry.card(card.card_id)
        power_id = str(power_def.get("id", card.card_id))
        initial_stacks = int(power_def.get("initial_stacks", 1))
        stacking = str(power_def.get("stacking", "stack"))

        existing = self.find_player_power(combat, power_id)
        if existing:
            if stacking == "stack":
                existing.stacks += initial_stacks
            elif stacking == "replace":
                existing.stacks = initial_stacks
            # ignore は何もしない。
            combat.log(f"Power更新: {card_def.get('name', power_id)} x{existing.stacks}")
            return existing

        power = PowerInstance(
            power_id=power_id,
            source_card_id=card.card_id,
            owner="player",
            stacks=initial_stacks,
            upgraded=card.upgraded,
        )
        combat.state.powers.append(power)
        combat.log(f"Power獲得: {card_def.get('name', power_id)} x{power.stacks}")
        return power

    def find_player_power(self, combat: "CombatSystem", power_id: str) -> PowerInstance | None:
        for power in combat.state.powers:
            if power.owner == "player" and power.power_id == power_id:
                return power
        return None

    def power_stacks(self, combat: "CombatSystem", power_id: str | None = None) -> int:
        if power_id:
            power = self.find_player_power(combat, power_id)
            return int(power.stacks) if power else 0
        return 0

    def power_def(self, power: PowerInstance) -> dict[str, Any]:
        if not power.source_card_id:
            return {}
        return self.power_def_for_card(power.source_card_id, power.upgraded)

    def power_def_for_card(self, card_id: str, upgraded: bool = False) -> dict[str, Any]:
        card_def = self.registry.card(card_id)
        power_def = deepcopy(card_def.get("power", {}) or {})
        if upgraded:
            upgrade_power = card_def.get("upgrade", {}).get("power", {}) or {}
            power_def = self._deep_merge(power_def, upgrade_power)
        return power_def

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = deepcopy(value)
        return merged
