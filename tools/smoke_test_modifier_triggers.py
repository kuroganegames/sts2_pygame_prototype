from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.models.entities import CardInstance
from spirelike.systems.card_modifier_system import CardModifierSystem
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = CardModifierSystem(registry)

run = create_run(registry, "wanderer", seed=665)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
attack = CardInstance("strike")
system.apply_modifier(attack, "cursed_edge")
combat.state.hand = [attack]
combat.state.energy = 3
enemy = combat.state.alive_enemies()[0]
hp_before = run.player.hp
combat.play_card(attack, enemy)
assert run.player.hp == hp_before - 2
print("OK")
