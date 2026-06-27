from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.profile.profile_data import ProfileState
from spirelike.systems.unlock_system import UnlockSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
profile = ProfileState()
profile.ensure_defaults()
system = UnlockSystem(registry)

assert system.is_unlocked(profile, "run_modifier", "rich_start")
assert not system.is_unlocked(profile, "run_modifier", "potion_belt")
system.ensure_initial_unlocks(profile)
assert system.is_unlocked(profile, "run_modifier", "potion_belt")
assert not system.is_unlocked(profile, "run_modifier", "stronger_enemies")
profile.summary["victories"] = 1
new = system.evaluate_unlocks(profile)
assert any(rule["target_id"] == "stronger_enemies" for rule in new)
assert system.is_unlocked(profile, "run_modifier", "stronger_enemies")
print("OK")
