from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
assert "alchemist" in registry.characters
alchemist = registry.character("alchemist")
assert alchemist["starting_relics"] == ["experimental_kit"]
for card_id in alchemist["starting_deck"]:
    assert card_id in registry.cards
for card_id in [
    "reagent",
    "glass_dart",
    "smoke_screen",
    "caustic_splash",
    "distill",
    "double_flask",
    "catalyst_field",
    "emergency_brew",
    "grand_mixture",
    "volatile_burst",
    "perfect_formula",
]:
    assert card_id in registry.cards
assert "experimental_kit" in registry.relics
assert "unlock_alchemist" in registry.unlock_rules
assert "alchemist_victory" in registry.achievements
print("OK")
