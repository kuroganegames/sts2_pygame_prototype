from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.profile.profile_data import ProfileState
from spirelike.systems.achievement_system import AchievementSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
profile = ProfileState()
profile.ensure_defaults()
system = AchievementSystem(registry)
assert not system.is_unlocked(profile, "first_victory")
assert not system.evaluate_achievements(profile)
profile.summary["victories"] = 1
new = system.evaluate_achievements(profile)
assert any(item["id"] == "first_victory" for item in new)
assert system.is_unlocked(profile, "first_victory")
assert not system.evaluate_achievements(profile)
print("OK")
