from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.difficulty_system import DifficultySystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = DifficultySystem(registry)

run0 = create_run(registry, "wanderer", seed=1200, run_config={"seed": 1200, "difficulty_level": 0})
assert system.enemy_hp_multiplier(run0) == 1.0
assert system.enemy_damage_multiplier(run0) == 1.0

run2 = create_run(registry, "wanderer", seed=1202, run_config={"seed": 1202, "difficulty_level": 2})
base_hp = registry.character("wanderer").get("max_hp", 70)
assert run2.player.max_hp == base_hp
assert run2.player.hp == int(base_hp * 0.8)
assert round(system.ancient_heal_missing_hp_multiplier(run2), 2) == 0.8

run4 = create_run(registry, "wanderer", seed=1204, run_config={"seed": 1204, "difficulty_level": 4})
assert run4.player.potion_slots == registry.character("wanderer").get("starting_potion_slots", 3) - 1

run5 = create_run(registry, "wanderer", seed=1205, run_config={"seed": 1205, "difficulty_level": 5})
assert any(card.card_id == "ascender_blight" for card in run5.player.deck)

run8 = create_run(registry, "wanderer", seed=1208, run_config={"seed": 1208, "difficulty_level": 8})
assert round(system.enemy_hp_multiplier(run8), 2) == 1.10

run9 = create_run(registry, "wanderer", seed=1209, run_config={"seed": 1209, "difficulty_level": 9})
assert round(system.enemy_damage_multiplier(run9), 2) == 1.10
print("OK")
