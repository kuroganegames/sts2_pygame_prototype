from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.models.entities import CardInstance
from spirelike.models.selection import CardSelectionRequest, CardSelectionResult
from spirelike.systems.card_operation_system import CardOperationSystem
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
ops = CardOperationSystem(registry)

run = create_run(registry, "wanderer", seed=556)
card = next(c for c in run.player.deck if registry.card(c.card_id).get("upgrade"))
request = CardSelectionRequest(
    title="upgrade",
    message="upgrade",
    source_zones=["master_deck"],
    operation={"type": "upgrade"},
)
ops.apply_result(run, request, CardSelectionResult(request.request_id, [card.instance_id]))
assert card.upgraded

remove_card = run.player.deck[0]
request = CardSelectionRequest(
    title="remove",
    message="remove",
    source_zones=["master_deck"],
    operation={"type": "remove"},
)
ops.apply_result(run, request, CardSelectionResult(request.request_id, [remove_card.instance_id]))
assert remove_card not in run.player.deck

transform_card = run.player.deck[0]
old_id = transform_card.card_id
request = CardSelectionRequest(
    title="transform",
    message="transform",
    source_zones=["master_deck"],
    operation={"type": "transform", "pool": {"character": True, "neutral": False, "exclude_basic": True}},
)
ops.apply_result(run, request, CardSelectionResult(request.request_id, [transform_card.instance_id]))
assert transform_card.card_id != old_id or len(registry.cards) > 1

run = create_run(registry, "wanderer", seed=557)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
combat.state.hand = [CardInstance("strike"), CardInstance("guard")]
combat.state.discard_pile = []
combat.state.exhaust_pile = []
discard_card = combat.state.hand[0]
request = CardSelectionRequest(
    title="discard",
    message="discard",
    source_zones=["hand"],
    operation={"type": "discard"},
)
ops.apply_result(run, request, CardSelectionResult(request.request_id, [discard_card.instance_id]), combat=combat)
assert discard_card in combat.state.discard_pile

exhaust_card = combat.state.hand[0]
request = CardSelectionRequest(
    title="exhaust",
    message="exhaust",
    source_zones=["hand"],
    operation={"type": "exhaust"},
)
ops.apply_result(run, request, CardSelectionResult(request.request_id, [exhaust_card.instance_id]), combat=combat)
assert exhaust_card in combat.state.exhaust_pile
print("OK")
