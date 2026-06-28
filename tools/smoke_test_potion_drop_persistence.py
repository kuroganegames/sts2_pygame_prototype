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
    save_system = SaveSystem(Path(tmp), registry)
    run = create_run(registry, "wanderer", seed=2005)
    run.flags["potion_drop_chance"] = 70.0
    save_system.save_run(run, current_scene="map", slot_id="slot_001")
    loaded, scene, payload = save_system.load_run("slot_001")
    assert scene == "map"
    assert loaded.flags["potion_drop_chance"] == 70.0
print("OK")
