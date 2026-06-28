from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.profile.profile_system import ProfileSystem
from spirelike.systems.unlock_system import UnlockSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

with tempfile.TemporaryDirectory() as tmp:
    profile_system = ProfileSystem(Path(tmp), registry)
    unlocks = UnlockSystem(registry)
    run = create_run(registry, "wanderer", seed=1701, run_config={"seed": 1701, "profile_eligible": True})
    profile_system.record_run_started(run)
    progression = profile_system.finalize_run(run, "victory")
    profile = profile_system.profile
    assert profile.achievements["first_victory"]["unlocked"] is True
    assert unlocks.is_unlocked(profile, "card", "focus_blade")
    assert any(rule.get("target_id") == "focus_blade" for rule in progression.new_content_unlocks)
    assert profile.achievements["first_unlock"]["unlocked"] is True
print("OK")
