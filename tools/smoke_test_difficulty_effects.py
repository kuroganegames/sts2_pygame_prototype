from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.systems.combat_system import CombatSystem
from spirelike.systems.difficulty_system import DifficultySystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = DifficultySystem(registry)

run0 = create_run(registry, "wanderer", seed=1200, run_config={"seed": 1200, "difficulty_level": 0})
assert system.enemy_hp_multiplier(run0) == 1.0

run1 = create_run(registry, "wanderer", seed=1201, run_config={"seed": 1201, "difficulty_level": 1})
assert round(system.enemy_hp_multiplier(run1), 2) == 1.10

run4 = create_run(registry, "wanderer", seed=1204, run_config={"seed": 1204, "difficulty_level": 4})
assert round(system.enemy_hp_multiplier(run4), 2) == 1.21

run2 = create_run(registry, "wanderer", seed=1202, run_config={"seed": 1202, "difficulty_level": 2})
assert round(system.enemy_damage_multiplier(run2), 2) == 1.10

run5 = create_run(registry, "wanderer", seed=1205, run_config={"seed": 1205, "difficulty_level": 5})
assert round(system.enemy_damage_multiplier(run5), 2) == 1.21

run3 = create_run(registry, "wanderer", seed=1203, run_config={"seed": 1203, "difficulty_level": 3})
base_hp = registry.character("wanderer").get("max_hp", 70)
assert run3.player.max_hp == base_hp - 5

combat0 = CombatSystem(registry, run0, ["slime_small"], RunRng(run0.seed).combat)
combat1 = CombatSystem(registry, run1, ["slime_small"], RunRng(run1.seed).combat)
assert combat1.state.enemies[0].max_hp >= combat0.state.enemies[0].max_hp
print("OK")
