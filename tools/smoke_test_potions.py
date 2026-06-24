from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.core.rng import RunRng
from spirelike.systems.combat_system import CombatSystem
from spirelike.systems.potion_system import PotionSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
assert registry.potions
run = create_run(registry, "wanderer", seed=24680)
potions = PotionSystem(registry)
assert potions.grant_potion(run, "fire_potion")
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
enemy = combat.state.alive_enemies()[0]
before = enemy.hp
assert potions.use_in_combat(combat, 0, enemy)
assert enemy.hp < before
assert run.player.potions[0] is None
print("OK")
print("enemy_hp:", before, "->", enemy.hp)
