from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.profile.profile_system import ProfileSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

with tempfile.TemporaryDirectory() as tmp:
    profile_system = ProfileSystem(Path(tmp), registry)
    profile = profile_system.profile
    profile.summary["runs_started"] = 1
    unlocked = profile_system.update_timeline_unlocks()
    assert "first_steps" in profile.timeline["unlocked_fragments"]
    profile.summary["victories"] = 1
    profile.bestiary["cultist"] = {"seen": True, "defeated": 3}
    profile.compendium["card_modifiers"]["sharp"] = {"seen": True, "applied": 1}
    unlocked = profile_system.update_timeline_unlocks()
    fragments = set(profile.timeline["unlocked_fragments"])
    assert {"first_victory", "cultist_study", "enchanted_blade"}.issubset(fragments)
print("OK")
