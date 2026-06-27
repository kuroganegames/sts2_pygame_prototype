from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.save.save_system import SaveSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    save_system = SaveSystem(root, registry)
    run = create_run(registry, "wanderer", seed=1004)
    save_system.save_run(run, current_scene="map", slot_id="slot_001")
    profile_path = root / "saves" / "profile.json"
    profile_path.write_text("{}", encoding="utf-8")
    assert save_system.slot_path("slot_001").exists()
    save_system.delete_slot("slot_001")
    assert not save_system.slot_path("slot_001").exists()
    assert profile_path.exists()
print("OK")
