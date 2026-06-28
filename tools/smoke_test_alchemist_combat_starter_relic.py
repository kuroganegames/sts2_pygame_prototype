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
run = create_run(registry, "alchemist", seed=1804)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
assert any(card.card_id == "reagent" for card in combat.state.hand)
print("OK")
