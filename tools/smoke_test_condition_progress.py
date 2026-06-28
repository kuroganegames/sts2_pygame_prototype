from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.profile.condition_progress import condition_progress
from spirelike.profile.profile_data import ProfileState

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
profile = ProfileState()
profile.ensure_defaults()

progress = condition_progress({"type": "victories_at_least", "amount": 1}, profile, registry)
assert progress.current == 0 and progress.required == 1 and not progress.complete
profile.summary["victories"] = 1
progress = condition_progress({"type": "victories_at_least", "amount": 1}, profile, registry)
assert progress.current == 1 and progress.complete

profile.bestiary["cultist"] = {"seen": True, "defeated": 2}
progress = condition_progress({"type": "enemy_defeated_count_at_least", "enemy": "cultist", "amount": 3}, profile, registry)
assert progress.current == 2 and progress.required == 3 and not progress.complete

profile.achievements["first_victory"] = {"unlocked": True}
progress = condition_progress({"type": "achievement_unlocked", "achievement": "first_victory"}, profile, registry)
assert progress.complete
print("OK")
