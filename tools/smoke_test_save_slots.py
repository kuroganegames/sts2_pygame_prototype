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
    run1 = create_run(registry, "wanderer", seed=1001)
    run2 = create_run(registry, "wanderer", seed=1002)
    save_system.save_run(run1, current_scene="map", slot_id="slot_001")
    save_system.save_run(run2, current_scene="map", slot_id="slot_002")

    slots = save_system.list_slots()
    assert len(slots) == 3
    assert slots[0].exists and slots[0].slot_id == "slot_001"
    assert slots[1].exists and slots[1].slot_id == "slot_002"
    assert not slots[2].exists

    loaded1, _, _ = save_system.load_run("slot_001")
    loaded2, _, _ = save_system.load_run("slot_002")
    assert loaded1.seed == 1001
    assert loaded2.seed == 1002
    assert loaded1.flags["save_slot_id"] == "slot_001"
    assert loaded2.flags["save_slot_id"] == "slot_002"
print("OK")
