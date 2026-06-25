from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

run = create_run(registry, "wanderer", seed=993)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
# RNGを少し進めてから保存する。
_ = [combat.rng.random() for _ in range(5)]
snapshot = combat.to_snapshot()
expected_next = combat.rng.random()
restored = CombatSystem(registry, run, [], RunRng(run.seed + 123).combat, snapshot=snapshot)
actual_next = restored.rng.random()
assert actual_next == expected_next
print("OK")
