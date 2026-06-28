from __future__ import annotations

from spirelike.content.loader import ContentRegistry
from spirelike.core.rng import RunRng
from spirelike.core.seed_utils import random_seed
from spirelike.models.entities import CardInstance, RelicInstance, PlayerState, RunState
from spirelike.models.run_config import RunConfig, run_config_to_dict
from spirelike.profile.run_metrics import RunMetricsSystem
from spirelike.systems.difficulty_system import DifficultySystem
from spirelike.systems.map_generator import MapGenerator
from spirelike.systems.run_modifier_system import RunModifierSystem


def create_run(
    registry: ContentRegistry,
    character_id: str,
    seed: int | None = None,
    run_config: RunConfig | dict | None = None,
) -> RunState:
    config_dict = run_config_to_dict(run_config)
    if seed is None:
        seed = config_dict.get("seed") or random_seed()
    seed = int(seed)
    config_dict["seed"] = seed
    config_dict["difficulty_level"] = int(config_dict.get("difficulty_level", 0))
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
    map_state = MapGenerator(registry).generate("act1", rng.map, run_config=config_dict)
    run = RunState(
        seed=seed,
        character_id=character_id,
        act=1,
        floor=0,
        player=player,
        map_state=map_state,
    )
    run.flags["run_config"] = config_dict
    DifficultySystem(registry).apply_run_start_effects(run)
    RunModifierSystem(registry).apply_run_start_modifiers(run, config_dict)
    RunMetricsSystem.ensure(run)
    run.add_message(f"Seed: {seed}")
    difficulty_level = int(config_dict.get("difficulty_level", 0))
    if difficulty_level > 0:
        run.add_message(f"Difficulty: {difficulty_level}")
    if config_dict.get("custom"):
        run.add_message("Custom Run: プロフィール集計対象外")
    return run
