from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
base_slots = int(registry.character("wanderer").get("starting_potion_slots", 3))
base_hp = int(registry.character("wanderer").get("max_hp", 70))

run0 = create_run(registry, "wanderer", seed=2100, run_config={"seed": 2100, "difficulty_level": 0})
assert run0.player.hp == base_hp
assert run0.player.potion_slots == base_slots
assert not any(card.card_id == "ascender_blight" for card in run0.player.deck)

run2 = create_run(registry, "wanderer", seed=2102, run_config={"seed": 2102, "difficulty_level": 2})
assert run2.player.hp == int(base_hp * 0.8)

run4 = create_run(registry, "wanderer", seed=2104, run_config={"seed": 2104, "difficulty_level": 4})
assert run4.player.potion_slots == base_slots - 1
assert len(run4.player.potions) == base_slots - 1

run5 = create_run(registry, "wanderer", seed=2105, run_config={"seed": 2105, "difficulty_level": 5})
assert any(card.card_id == "ascender_blight" for card in run5.player.deck)
print("OK")
