from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.models.entities import CardInstance
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "alchemist", seed=1803)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
run.player.potions = [None for _ in range(run.player.potion_slots)]
combat.state.hand = [CardInstance("emergency_brew")]
card = combat.state.hand[0]
assert combat.play_card(card, None)
assert any(potion is not None for potion in run.player.potions)
print("OK")
