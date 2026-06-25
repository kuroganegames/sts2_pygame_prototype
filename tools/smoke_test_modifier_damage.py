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

run = create_run(registry, "wanderer", seed=661)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
enemy = combat.state.alive_enemies()[0]
attack = CardInstance("strike")
system.apply_modifier(attack, "sharp")
hp_before = enemy.hp
combat.deal_damage(run.player, enemy, 6, registry.card("strike"), attack)
assert hp_before - enemy.hp == 9

run = create_run(registry, "wanderer", seed=662)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
run.player.block = 0
guard = CardInstance("guard")
system.apply_modifier(guard, "steady")
combat.state.hand = [guard]
combat.state.energy = 3
combat.play_card(guard, None)
assert run.player.block == 8

run = create_run(registry, "wanderer", seed=663)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
brittle = CardInstance("strike")
system.apply_modifier(brittle, "brittle")
combat.state.hand = [brittle]
combat.state.energy = 3
enemy = combat.state.alive_enemies()[0]
combat.play_card(brittle, enemy)
assert brittle in combat.state.exhaust_pile
print("OK")
