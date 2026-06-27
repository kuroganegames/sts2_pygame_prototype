from __future__ import annotations

from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, RelicInstance, RunState


class RunModifierSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def selected_modifier_defs(self, config: dict[str, Any] | None) -> list[dict[str, Any]]:
        config = config or {}
        result: list[dict[str, Any]] = []
        for modifier_id in config.get("selected_modifiers", []) or []:
            if modifier_id in self.registry.run_modifiers:
                result.append(self.registry.run_modifier(modifier_id))
        return result

    def apply_run_start_modifiers(self, run_state: RunState, config: dict[str, Any] | None) -> None:
        for modifier_def in self.selected_modifier_defs(config):
            for effect in modifier_def.get("effects", []) or []:
                self.apply_run_start_effect(run_state, modifier_def, effect)

    def apply_run_start_effect(self, run_state: RunState, modifier_def: dict[str, Any], effect: dict[str, Any]) -> None:
        effect_type = effect.get("type")
        player = run_state.player
        if effect_type == "gain_gold":
            amount = int(effect.get("amount", 0))
            player.gold += amount
            run_state.add_message(f"{modifier_def.get('name', 'Modifier')}: ゴールド +{amount}")
        elif effect_type == "add_potion_slot":
            amount = max(0, int(effect.get("amount", 1)))
            player.potion_slots += amount
            player.potions.extend([None for _ in range(amount)])
            run_state.add_message(f"{modifier_def.get('name', 'Modifier')}: ポーションスロット +{amount}")
        elif effect_type == "add_card_to_deck":
            card_id = str(effect.get("card"))
            if card_id in self.registry.cards:
                player.deck.append(CardInstance(card_id=card_id, upgraded=bool(effect.get("upgraded", False))))
                run_state.add_message(f"{modifier_def.get('name', 'Modifier')}: カード追加 {self.registry.card(card_id).get('name', card_id)}")
        elif effect_type == "gain_relic":
            relic_id = str(effect.get("relic"))
            if relic_id in self.registry.relics and not player.has_relic(relic_id):
                player.relics.append(RelicInstance(relic_id=relic_id))
                run_state.add_message(f"{modifier_def.get('name', 'Modifier')}: レリック獲得 {self.registry.relic(relic_id).get('name', relic_id)}")

    def enemy_hp_multiplier(self, run_state: RunState) -> float:
        config = run_state.flags.get("run_config", {}) or {}
        multiplier = 1.0
        for modifier_def in self.selected_modifier_defs(config):
            for effect in modifier_def.get("effects", []) or []:
                if effect.get("type") == "enemy_hp_multiplier":
                    multiplier *= float(effect.get("multiplier", 1.0))
        return multiplier
