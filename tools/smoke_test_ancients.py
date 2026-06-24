from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.core.rng import RunRng
from spirelike.systems.ancient_system import AncientSystem
from spirelike.systems.combat_system import CombatSystem
from spirelike.systems.run_effects import RunEffectExecutor

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
assert registry.ancients
run = create_run(registry, "wanderer", seed=13579)
ancients = AncientSystem(registry)
ancient_def = registry.ancient("old_smith")
choice = ancients.find_choice(ancient_def, "battle_temper")
assert choice
ancients.apply_choice(run, ancient_def, choice, RunEffectExecutor(registry, RunRng(run.seed).event))
assert run.ancient_blessings
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
assert run.player.statuses.get("strength", 0) >= 1
print("OK")
print("blessings:", [(b.ancient_id, b.choice_id) for b in run.ancient_blessings])
print("player_statuses:", run.player.statuses)
