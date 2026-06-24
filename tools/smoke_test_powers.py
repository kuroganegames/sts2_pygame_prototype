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

run = create_run(registry, "wanderer", seed=444)
run.player.deck = [CardInstance("guard_stance"), CardInstance("strike")]
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
combat.state.hand = [CardInstance("guard_stance"), CardInstance("strike")]
combat.state.draw_pile = []
combat.state.discard_pile = []
combat.state.energy = 3
power_card = combat.state.hand[0]
combat.play_card(power_card, None)
assert combat.state.powers and combat.state.powers[0].power_id == "guard_stance"
assert not any(card.card_id == "guard_stance" for card in combat.state.discard_pile)

block_before = run.player.block
attack = next(card for card in combat.state.hand if card.card_id == "strike")
enemy = combat.state.alive_enemies()[0]
combat.play_card(attack, enemy)
assert run.player.block >= block_before + 2

run = create_run(registry, "wanderer", seed=445)
run.player.deck = [CardInstance("opening_focus")]
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
combat.state.hand = [CardInstance("opening_focus")]
combat.state.energy = 3
combat.play_card(combat.state.hand[0], None)
run.player.block = 0
combat.start_player_turn()
assert run.player.block >= 1
print("OK")
