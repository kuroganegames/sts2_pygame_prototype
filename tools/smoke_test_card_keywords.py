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

# Innate: initial hand should include opening_focus even in a large deck.
run = create_run(registry, "wanderer", seed=333)
run.player.deck = [CardInstance("strike") for _ in range(12)] + [CardInstance("opening_focus")]
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
assert any(card.card_id == "opening_focus" for card in combat.state.hand), [c.card_id for c in combat.state.hand]

# Exhaust after play.
run = create_run(registry, "wanderer", seed=334)
run.player.deck = [CardInstance("finishing_cut")]
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
card = next(card for card in combat.state.hand if card.card_id == "finishing_cut")
enemy = combat.state.alive_enemies()[0]
combat.play_card(card, enemy)
assert any(card.card_id == "finishing_cut" for card in combat.state.exhaust_pile)

# Retain should keep card in hand at player turn end.
run = create_run(registry, "wanderer", seed=335)
run.player.deck = [CardInstance("held_guard")]
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
combat.state.hand = [CardInstance("held_guard")]
combat.state.draw_pile = []
combat.state.discard_pile = []
combat.end_player_turn()
assert any(card.card_id == "held_guard" for card in combat.state.hand)

# Ethereal should exhaust at player turn end.
run = create_run(registry, "wanderer", seed=336)
run.player.deck = [CardInstance("ghost_guard")]
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
combat.state.hand = [CardInstance("ghost_guard")]
combat.state.draw_pile = []
combat.state.discard_pile = []
combat.end_player_turn()
assert any(card.card_id == "ghost_guard" for card in combat.state.exhaust_pile)

# Unplayable should fail can_play.
run = create_run(registry, "wanderer", seed=337)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
ok, reason = combat.can_play(CardInstance("wound"))
assert not ok and reason == "使用不可"
print("OK")
