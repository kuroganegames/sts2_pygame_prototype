from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
for card_id in ["focus_blade", "guard_stance", "venom_tip"]:
    assert card_id in registry.cards
    assert registry.cards[card_id].image_path is not None
for relic_id in ["cultist_charm", "steady_gear"]:
    assert relic_id in registry.relics
    assert registry.relics[relic_id].image_path is not None
assert "swift_potion" in registry.potions
assert registry.potions["swift_potion"].image_path is not None
assert "glass_path" in registry.run_modifiers
for unlock_id in [
    "unlock_focus_blade",
    "unlock_guard_stance",
    "unlock_venom_tip",
    "unlock_cultist_charm",
    "unlock_steady_gear",
    "unlock_swift_potion",
    "unlock_glass_path",
]:
    assert unlock_id in registry.unlock_rules
print("OK")
