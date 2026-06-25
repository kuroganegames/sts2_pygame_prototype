from __future__ import annotations

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import RunState


class SaveValidationError(ValueError):
    pass


def validate_loaded_run(run_state: RunState, registry: ContentRegistry) -> list[str]:
    warnings: list[str] = []

    if run_state.character_id not in registry.characters:
        raise SaveValidationError(f"Unknown character_id in save: {run_state.character_id}")

    if run_state.map_state.act_id not in registry.maps:
        raise SaveValidationError(f"Unknown map act_id in save: {run_state.map_state.act_id}")

    valid_deck = []
    for card in run_state.player.deck:
        if card.card_id not in registry.cards:
            warnings.append(f"Removed missing card from deck: {card.card_id}")
            continue
        card.modifiers = [
            modifier
            for modifier in card.modifiers
            if modifier.modifier_id in registry.card_modifiers
        ]
        valid_deck.append(card)
    run_state.player.deck = valid_deck

    run_state.player.relics = [
        relic
        for relic in run_state.player.relics
        if relic.relic_id in registry.relics
    ]

    fixed_potions = []
    for potion in run_state.player.potions:
        if potion is None:
            fixed_potions.append(None)
        elif potion.potion_id in registry.potions:
            fixed_potions.append(potion)
        else:
            warnings.append(f"Removed missing potion from slot: {potion.potion_id}")
            fixed_potions.append(None)
    run_state.player.potions = fixed_potions[: run_state.player.potion_slots]
    if len(run_state.player.potions) < run_state.player.potion_slots:
        run_state.player.potions.extend([None] * (run_state.player.potion_slots - len(run_state.player.potions)))

    valid_blessings = []
    for blessing in run_state.ancient_blessings:
        if blessing.ancient_id not in registry.ancients:
            warnings.append(f"Removed missing ancient blessing: {blessing.ancient_id}")
            continue
        ancient = registry.ancient(blessing.ancient_id)
        choices = ancient.get("choices", []) or []
        if not any(choice.get("id") == blessing.choice_id for choice in choices):
            warnings.append(f"Removed missing ancient choice: {blessing.ancient_id}.{blessing.choice_id}")
            continue
        valid_blessings.append(blessing)
    run_state.ancient_blessings = valid_blessings

    known_statuses = set(registry.statuses)
    run_state.player.statuses = {
        status: stacks
        for status, stacks in run_state.player.statuses.items()
        if status in known_statuses
    }

    return warnings


def validate_combat_snapshot(snapshot: dict, registry: ContentRegistry) -> list[str]:
    warnings: list[str] = []
    if not isinstance(snapshot, dict):
        raise SaveValidationError("Combat snapshot must be a mapping")

    state = snapshot.get("state")
    if not isinstance(state, dict):
        raise SaveValidationError("Combat snapshot has no state")

    known_statuses = set(registry.statuses)
    for enemy in state.get("enemies", []) or []:
        enemy_id = enemy.get("enemy_id")
        if enemy_id not in registry.enemies:
            raise SaveValidationError(f"Unknown enemy in combat save: {enemy_id}")
        enemy["statuses"] = {
            status: stacks
            for status, stacks in (enemy.get("statuses", {}) or {}).items()
            if status in known_statuses
        }

    for zone in ["draw_pile", "hand", "discard_pile", "exhaust_pile", "limbo"]:
        cleaned_cards = []
        for card in state.get(zone, []) or []:
            card_id = card.get("card_id")
            if card_id not in registry.cards:
                warnings.append(f"Removed missing combat card from {zone}: {card_id}")
                continue
            card["modifiers"] = [
                modifier
                for modifier in card.get("modifiers", []) or []
                if (modifier.get("modifier_id") if isinstance(modifier, dict) else str(modifier)) in registry.card_modifiers
            ]
            cleaned_cards.append(card)
        state[zone] = cleaned_cards

    cleaned_powers = []
    for power in state.get("powers", []) or []:
        source_card_id = power.get("source_card_id")
        if source_card_id and source_card_id not in registry.cards:
            warnings.append(f"Removed power with missing source card: {source_card_id}")
            continue
        cleaned_powers.append(power)
    state["powers"] = cleaned_powers
    return warnings
