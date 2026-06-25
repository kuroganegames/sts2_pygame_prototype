from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.core.rng import RunRng
from spirelike.systems.actions import DamageAction, DrawCardsAction, ApplyStatusAction
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=222)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
enemy = combat.state.alive_enemies()[0]
start_hp = enemy.hp
combat.enqueue_action(DamageAction(run.player, enemy, 3, {"type": "attack"}))
combat.resolve_actions()
assert enemy.hp < start_hp
hand_before = len(combat.state.hand)
combat.enqueue_action(DrawCardsAction(1))
combat.resolve_actions()
assert len(combat.state.hand) >= hand_before
combat.enqueue_action(ApplyStatusAction(enemy, "weak", 1))
combat.resolve_actions()
assert enemy.statuses.get("weak", 0) >= 1
print("OK")
