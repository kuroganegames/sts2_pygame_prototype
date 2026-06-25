from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.models.entities import PotionInstance
from spirelike.save.save_data import CURRENT_SAVE_SCHEMA_VERSION
from spirelike.save.save_system import SaveSystem
from spirelike.save.serializer import run_state_to_dict
from spirelike.systems.card_modifier_system import CardModifierSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=771)
CardModifierSystem(registry).apply_modifier(run.player.deck[0], "sharp")
run.player.deck[0].modifiers[0].modifier_id = "missing_modifier"
missing_card = run.player.add_card("strike")
missing_card.card_id = "missing_card"
run.player.potions[0] = PotionInstance("missing_potion")

data = {
    "schema_version": CURRENT_SAVE_SCHEMA_VERSION,
    "game_version": "test",
    "saved_at": "now",
    "current_scene": "map",
    "scene_payload": {},
    "run": run_state_to_dict(run),
    "rng_state": {},
    "content_snapshot": {},
}

with tempfile.TemporaryDirectory() as tmp:
    save_system = SaveSystem(Path(tmp), registry)
    save_system.save_dir.mkdir(parents=True, exist_ok=True)
    save_system.default_path.write_text(json.dumps(data), encoding="utf-8")
    loaded, _, _ = save_system.load_run()

assert all(card.card_id != "missing_card" for card in loaded.player.deck)
assert not loaded.player.deck[0].modifiers
assert loaded.player.potions[0] is None
print("OK")
