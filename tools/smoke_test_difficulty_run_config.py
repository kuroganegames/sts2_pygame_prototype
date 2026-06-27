from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.models.run_config import RunConfig, run_config_from_dict, run_config_to_dict
from spirelike.save.save_system import SaveSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

config = RunConfig(mode="seeded", seed=1400, difficulty_level=3)
data = run_config_to_dict(config)
assert data["difficulty_level"] == 3
assert run_config_from_dict(data).difficulty_level == 3
assert run_config_to_dict({"seed": 1401})["difficulty_level"] == 0

run = create_run(registry, "wanderer", run_config=data)
assert run.flags["run_config"]["difficulty_level"] == 3

with tempfile.TemporaryDirectory() as tmp:
    save_system = SaveSystem(Path(tmp), registry)
    save_system.save_run(run, current_scene="map", slot_id="slot_001")
    slot = save_system.list_slots()[0]
    assert slot.difficulty_level == 3
print("OK")
