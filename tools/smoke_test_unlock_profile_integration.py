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
    standard = create_run(registry, "wanderer", seed=1501, run_config={"seed": 1501, "profile_eligible": True})
    profile_system.record_run_started(standard)
    profile_system.finalize_run(standard, "victory")
    assert unlocks.is_unlocked(profile_system.profile, "run_modifier", "stronger_enemies")

with tempfile.TemporaryDirectory() as tmp:
    profile_system = ProfileSystem(Path(tmp), registry)
    unlocks = UnlockSystem(registry)
    custom = create_run(
        registry,
        "wanderer",
        seed=1502,
        run_config={
            "seed": 1502,
            "custom": True,
            "selected_modifiers": ["rich_start"],
            "profile_eligible": False,
        },
    )
    profile_system.record_run_started(custom)
    profile_system.finalize_run(custom, "victory")
    assert not unlocks.is_unlocked(profile_system.profile, "run_modifier", "stronger_enemies")
print("OK")
