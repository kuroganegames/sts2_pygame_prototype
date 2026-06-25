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

run = create_run(registry, "wanderer", seed=990)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
combat.state.energy = 2
combat.state.log.append("snapshot test")
snapshot = combat.to_snapshot()
restored = CombatSystem(registry, run, [], RunRng(run.seed + 99).combat, snapshot=snapshot)

assert len(restored.state.enemies) == len(combat.state.enemies)
assert restored.state.energy == 2
assert restored.state.turn_number == combat.state.turn_number
assert [c.card_id for c in restored.state.hand] == [c.card_id for c in combat.state.hand]
assert [c.card_id for c in restored.state.draw_pile] == [c.card_id for c in combat.state.draw_pile]
assert restored.state.log[-2] == "snapshot test"
assert restored.state.log[-1] == "戦闘を再開"
print("OK")
