from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.save.save_data import CURRENT_SAVE_SCHEMA_VERSION
from spirelike.save.save_system import SaveSystem
from spirelike.save.serializer import run_state_to_dict

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=1003)

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
    slots = save_system.list_slots()
    assert slots[0].exists
    assert save_system.slot_path("slot_001").exists()
    assert (save_system.save_dir / "save_001.migrated.bak").exists()
    loaded, scene, payload = save_system.load_run("slot_001")

assert scene == "map"
assert loaded.seed == 1003
assert loaded.flags["save_slot_id"] == "slot_001"
print("OK")
