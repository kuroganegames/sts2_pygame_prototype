from __future__ import annotations

from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, RunState


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
        return self.selected_level_from_config(config)

    def selected_level_from_config(self, config: dict[str, Any] | None) -> int:
        config = config or {}
        return max(0, int(config.get("difficulty_level", 0)))

    def effects_up_to(self, level: int) -> list[dict[str, Any]]:
        effects: list[dict[str, Any]] = []
        for data in self.all_levels():
            if int(data.get("level", 0)) <= int(level):
                effects.extend(data.get("effects", []) or [])
        return effects

    def effects_for_run(self, run_state: RunState) -> list[dict[str, Any]]:
        return self.effects_up_to(self.selected_level(run_state))

    def effects_for_config(self, config: dict[str, Any] | None) -> list[dict[str, Any]]:
        return self.effects_up_to(self.selected_level_from_config(config))

    def has_effect(self, run_state: RunState, effect_type: str) -> bool:
        return any(effect.get("type") == effect_type for effect in self.effects_for_run(run_state))

    def enemy_hp_multiplier(self, run_state: RunState) -> float:
        multiplier = 1.0
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "enemy_hp_multiplier":
                multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier

    def enemy_damage_multiplier(self, run_state: RunState) -> float:
        multiplier = 1.0
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "enemy_damage_multiplier":
                multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier

    def gold_reward_multiplier(self, run_state: RunState, source: str) -> float:
        multiplier = 1.0
        for effect in self.effects_for_run(run_state):
            if effect.get("type") != "gold_reward_multiplier":
                continue
            sources = effect.get("source", [])
            if isinstance(sources, str):
                sources = [sources]
            if not sources or source in sources:
                multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier

    def map_weight_multiplier_for_config(self, config: dict[str, Any] | None, node_type: str) -> float:
        multiplier = 1.0
        for effect in self.effects_for_config(config):
            if effect.get("type") == "map_weight_multiplier" and effect.get("node_type") == node_type:
                multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier

    def map_weight_multiplier(self, run_state: RunState, node_type: str) -> float:
        multiplier = 1.0
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "map_weight_multiplier" and effect.get("node_type") == node_type:
                multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier

    def potion_slot_delta(self, run_state: RunState) -> int:
        total = 0
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "potion_slot_delta":
                total += int(effect.get("amount", 0))
        return total

    def starting_hp_multiplier(self, run_state: RunState) -> float:
        multiplier = 1.0
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "starting_hp_multiplier":
                multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier

    def ancient_heal_missing_hp_multiplier(self, run_state: RunState) -> float:
        multiplier = 1.0
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "ancient_heal_missing_hp_multiplier":
                multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier

    def ancient_missing_hp_heal_amount(self, run_state: RunState) -> int:
        missing = max(0, run_state.player.max_hp - run_state.player.hp)
        return max(0, int(missing * self.ancient_heal_missing_hp_multiplier(run_state)))

    def card_remove_cost_config(self, run_state: RunState) -> dict[str, int]:
        config = {"base": 75, "step": 25}
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "card_remove_cost":
                config["base"] = int(effect.get("base", config["base"]))
                config["step"] = int(effect.get("step", config["step"]))
        return config

    def depletion_enabled(self, run_state: RunState) -> bool:
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "card_reward_depletion":
                return bool(effect.get("enabled", True))
        return False

    def double_boss_enabled(self, run_state: RunState, act: int) -> bool:
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "double_boss" and int(effect.get("act", 3)) == int(act):
                return True
        return False

    def apply_run_start_effects(self, run_state: RunState) -> None:
        player = run_state.player

        total_max_hp_delta = 0
        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "player_max_hp_delta":
                total_max_hp_delta += int(effect.get("amount", 0))
        if total_max_hp_delta:
            player.max_hp = max(1, player.max_hp + total_max_hp_delta)
            player.hp = min(player.hp, player.max_hp)
            run_state.add_message(f"Difficulty: 最大HP {total_max_hp_delta:+}")

        hp_multiplier = self.starting_hp_multiplier(run_state)
        if hp_multiplier != 1.0:
            player.hp = max(1, min(player.max_hp, int(player.max_hp * hp_multiplier)))
            run_state.add_message(f"Difficulty: 初期HP {int(hp_multiplier * 100)}%")

        slot_delta = self.potion_slot_delta(run_state)
        if slot_delta:
            player.potion_slots = max(0, player.potion_slots + slot_delta)
            player.potions = player.potions[: player.potion_slots]
            if len(player.potions) < player.potion_slots:
                player.potions.extend([None] * (player.potion_slots - len(player.potions)))
            run_state.add_message(f"Difficulty: ポーションスロット {slot_delta:+}")

        for effect in self.effects_for_run(run_state):
            if effect.get("type") == "add_card_to_deck":
                card_id = str(effect.get("card", ""))
                if card_id in self.registry.cards:
                    player.deck.append(CardInstance(card_id=card_id))
                    run_state.add_message(f"Difficulty: カード追加 {self.registry.card(card_id).get('name', card_id)}")

        if self.double_boss_enabled(run_state, 3):
            run_state.flags["double_boss_enabled"] = True
