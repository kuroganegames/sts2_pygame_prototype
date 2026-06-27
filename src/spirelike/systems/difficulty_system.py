from __future__ import annotations

from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import RunState


class DifficultySystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def all_levels(self) -> list[dict[str, Any]]:
        return sorted(
            [item.data for item in self.registry.difficulty_levels.values()],
            key=lambda data: int(data.get("level", 0)),
        )

    def level_def(self, level: int) -> dict[str, Any] | None:
        for data in self.all_levels():
            if int(data.get("level", 0)) == int(level):
                return data
        return None

    def max_defined_level(self) -> int:
        levels = [int(data.get("level", 0)) for data in self.all_levels()]
        return max(levels) if levels else 0

    def selected_level(self, run_state: RunState) -> int:
        config = run_state.flags.get("run_config", {}) or {}
        return max(0, int(config.get("difficulty_level", 0)))

    def effects_up_to(self, level: int) -> list[dict[str, Any]]:
        effects: list[dict[str, Any]] = []
        for data in self.all_levels():
            if int(data.get("level", 0)) <= int(level):
                effects.extend(data.get("effects", []) or [])
        return effects

    def enemy_hp_multiplier(self, run_state: RunState) -> float:
        multiplier = 1.0
        for effect in self.effects_up_to(self.selected_level(run_state)):
            if effect.get("type") == "enemy_hp_multiplier":
                multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier

    def enemy_damage_multiplier(self, run_state: RunState) -> float:
        multiplier = 1.0
        for effect in self.effects_up_to(self.selected_level(run_state)):
            if effect.get("type") == "enemy_damage_multiplier":
                multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier

    def apply_run_start_effects(self, run_state: RunState) -> None:
        total_max_hp_delta = 0
        for effect in self.effects_up_to(self.selected_level(run_state)):
            if effect.get("type") == "player_max_hp_delta":
                total_max_hp_delta += int(effect.get("amount", 0))
        if total_max_hp_delta:
            player = run_state.player
            player.max_hp = max(1, player.max_hp + total_max_hp_delta)
            player.hp = min(player.hp, player.max_hp)
            run_state.add_message(f"Difficulty: 最大HP {total_max_hp_delta:+}")
