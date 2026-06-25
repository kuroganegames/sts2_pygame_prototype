from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.models.selection import CardSelectionRequest
from spirelike.systems.actions import DrawCardsAction
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=992)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)

ok, reason = combat.can_save_combat()
assert ok, reason

combat.state.pending_selection = CardSelectionRequest("test", "test", ["hand"])
ok, reason = combat.can_save_combat()
assert not ok and "カード選択" in reason
combat.state.pending_selection = None

combat.enqueue_action(DrawCardsAction(1))
ok, reason = combat.can_save_combat()
assert not ok and "未解決Action" in reason
combat.action_queue.clear()

combat.state.limbo.append(combat.state.hand[0])
ok, reason = combat.can_save_combat()
assert not ok and "カード解決中" in reason
combat.state.limbo.clear()

combat.state.outcome = "victory"
ok, reason = combat.can_save_combat()
assert not ok and "戦闘終了" in reason
print("OK")
