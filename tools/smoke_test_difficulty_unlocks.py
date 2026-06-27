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
    assert profile_system._character_stats("wanderer")["highest_difficulty_unlocked"] == 0

    run0 = create_run(registry, "wanderer", seed=1300, run_config={"seed": 1300, "difficulty_level": 0})
    profile_system.record_run_started(run0)
    profile_system.finalize_run(run0, "victory")
    assert profile_system.profile.characters["wanderer"]["highest_difficulty_unlocked"] == 1

    run1_defeat = create_run(registry, "wanderer", seed=1301, run_config={"seed": 1301, "difficulty_level": 1})
    profile_system.record_run_started(run1_defeat)
    profile_system.finalize_run(run1_defeat, "defeat")
    assert profile_system.profile.characters["wanderer"]["highest_difficulty_unlocked"] == 1

    run1_victory = create_run(registry, "wanderer", seed=1302, run_config={"seed": 1302, "difficulty_level": 1})
    profile_system.record_run_started(run1_victory)
    profile_system.finalize_run(run1_victory, "victory")
    assert profile_system.profile.characters["wanderer"]["highest_difficulty_unlocked"] == 2

    custom = create_run(
        registry,
        "wanderer",
        seed=1303,
        run_config={
            "seed": 1303,
            "difficulty_level": 2,
            "custom": True,
            "selected_modifiers": ["rich_start"],
            "profile_eligible": False,
        },
    )
    profile_system.record_run_started(custom)
    profile_system.finalize_run(custom, "victory")
    assert profile_system.profile.characters["wanderer"]["highest_difficulty_unlocked"] == 2
print("OK")
