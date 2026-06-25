from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.models.entities import CardInstance
from spirelike.models.selection import CardSelectionResult
from spirelike.systems.combat_system import CombatSystem
from spirelike.systems.run_effects import RunEffectExecutor

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

run = create_run(registry, "wanderer", seed=558)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
combat.state.hand = [CardInstance("consume_focus"), CardInstance("strike")]
combat.state.draw_pile = [CardInstance("guard")]
combat.state.discard_pile = []
combat.state.exhaust_pile = []
combat.state.energy = 3
card = next(c for c in combat.state.hand if c.card_id == "consume_focus")
combat.play_card(card, None)
assert combat.state.pending_selection is not None
target = next(c for c in combat.state.hand if c.card_id == "strike")
request_id = combat.state.pending_selection.request_id
combat.complete_card_selection(CardSelectionResult(request_id, [target.instance_id]))
assert target in combat.state.exhaust_pile
assert combat.state.pending_selection is None

run = create_run(registry, "wanderer", seed=559)
executor = RunEffectExecutor(registry, RunRng(run.seed).event)
effect = {
    "type": "upgrade_card",
    "selector": {
        "zones": ["master_deck"],
        "count": 1,
        "player_choice": True,
        "filter": {"can_upgrade": True},
    },
}
completed = executor.execute_many(run, [effect, {"type": "gain_gold", "amount": 5}])
assert not completed
assert run.pending_selection is not None
selected = run.player.deck[0]
# ensure selected can upgrade
for candidate in run.player.deck:
    if registry.card(candidate.card_id).get("upgrade") and not candidate.upgraded:
        selected = candidate
        break
from spirelike.systems.card_operation_system import CardOperationSystem
req = run.pending_selection
CardOperationSystem(registry).apply_result(run, req, CardSelectionResult(req.request_id, [selected.instance_id]))
run.pending_selection = None
remaining = list(run.pending_effects)
run.pending_effects = []
executor.execute_many(run, remaining)
assert selected.upgraded
assert run.player.gold >= 104
print("OK")
