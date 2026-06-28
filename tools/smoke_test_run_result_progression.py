from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.profile.profile_system import ProfileSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

with tempfile.TemporaryDirectory() as tmp:
    profile_system = ProfileSystem(Path(tmp), registry)
    run = create_run(registry, "wanderer", seed=1601, run_config={"seed": 1601, "profile_eligible": True})
    profile_system.record_run_started(run)
    progression = profile_system.finalize_run(run, "victory")
    assert any(rule.get("target_id") == "stronger_enemies" for rule in progression.new_content_unlocks)
    assert any(item.get("id") == "first_victory" for item in progression.new_achievements)
    assert progression.notifications
    assert profile_system.profile.notifications
print("OK")
