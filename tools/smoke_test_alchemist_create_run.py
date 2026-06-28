from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "alchemist", seed=1801)
assert run.character_id == "alchemist"
assert run.player.character_id == "alchemist"
assert run.player.potion_slots == 4
assert len(run.player.potions) == 4
assert [relic.relic_id for relic in run.player.relics] == ["experimental_kit"]
assert len(run.player.deck) == 10
assert {card.card_id for card in run.player.deck} >= {"alchemist_strike", "alchemist_guard", "vial_toss", "quick_brew"}
print("OK")
