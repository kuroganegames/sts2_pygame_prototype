from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.core.rng import RunRng
from spirelike.systems.map_generator import MapGenerator
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=12345)
first = run.map_state.available_nodes()[0]
enemy_ids = MapGenerator(registry).choose_encounter(run.map_state.act_id, first.node_type, RunRng(run.seed).combat)
combat = CombatSystem(registry, run, enemy_ids, RunRng(run.seed).combat)
assert combat.state.hand
assert combat.state.alive_enemies()
print("OK")
print("hand:", [c.card_id for c in combat.state.hand])
print("enemies:", [(e.enemy_id, e.hp, e.next_move) for e in combat.state.enemies])
