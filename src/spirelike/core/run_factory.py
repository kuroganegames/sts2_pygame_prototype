from __future__ import annotations

import time

from spirelike.content.loader import ContentRegistry
from spirelike.core.rng import RunRng
from spirelike.models.entities import CardInstance, RelicInstance, PlayerState, RunState
from spirelike.profile.run_metrics import RunMetricsSystem
from spirelike.systems.map_generator import MapGenerator


def create_run(registry: ContentRegistry, character_id: str, seed: int | None = None) -> RunState:
    if seed is None:
        seed = int(time.time() * 1000) % 2_147_483_647
    rng = RunRng(seed)
    character = registry.character(character_id)
    deck = [CardInstance(card_id=card_id) for card_id in character.get("starting_deck", [])]
    relics = [RelicInstance(relic_id=relic_id) for relic_id in character.get("starting_relics", [])]
    potion_slots = int(character.get("starting_potion_slots", 3))
    player = PlayerState(
        character_id=character_id,
        hp=int(character.get("starting_hp", character.get("max_hp", 70))),
        max_hp=int(character.get("max_hp", 70)),
        gold=int(character.get("starting_gold", 0)),
        base_energy=int(character.get("base_energy", 3)),
        deck=deck,
        relics=relics,
        potion_slots=potion_slots,
        potions=[None for _ in range(potion_slots)],
    )
    map_state = MapGenerator(registry).generate("act1", rng.map)
    run = RunState(
        seed=seed,
        character_id=character_id,
        act=1,
        floor=0,
        player=player,
        map_state=map_state,
    )
    RunMetricsSystem.ensure(run)
    run.add_message(f"Seed: {seed}")
    return run
