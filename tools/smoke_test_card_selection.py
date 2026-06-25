from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.models.selection import CardSelectionRequest
from spirelike.systems.card_selection_system import CardSelectionSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=555)
system = CardSelectionSystem(registry)

request = CardSelectionRequest(
    title="test",
    message="test",
    source_zones=["master_deck"],
    filter={"types": ["attack"]},
)
candidates = system.collect_candidates(run, request)
assert candidates
assert all(registry.card(c.card.card_id).get("type") == "attack" for c in candidates)

upgrade_request = CardSelectionRequest(
    title="upgrade",
    message="upgrade",
    source_zones=["master_deck"],
    filter={"can_upgrade": True},
)
upgrade_candidates = system.collect_candidates(run, upgrade_request)
assert upgrade_candidates
assert all(not c.card.upgraded and registry.card(c.card.card_id).get("upgrade") for c in upgrade_candidates)
print("OK")
