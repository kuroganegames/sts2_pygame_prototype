from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.profile.condition_evaluator import condition_met
from spirelike.profile.profile_data import ProfileState

profile = ProfileState()
profile.ensure_defaults()
profile.summary["victories"] = 1
profile.characters["wanderer"] = {
    "victories": 2,
    "highest_difficulty_victory": 1,
    "highest_difficulty_unlocked": 2,
}
profile.bestiary["cultist"] = {"seen": True, "defeated": 3}
profile.compendium["cards"]["strike"] = {"seen": True, "acquired": 1, "played": 5}
profile.compendium["potions"]["fire_potion"] = {"seen": True, "used": 2}
profile.timeline["unlocked_fragments"] = ["first_steps"]

assert condition_met(profile, {"type": "victories_at_least", "amount": 1})
assert condition_met(profile, {"type": "character_difficulty_victory_at_least", "character": "wanderer", "level": 1})
assert condition_met(profile, {"type": "enemy_defeated_count_at_least", "enemy": "cultist", "amount": 3})
assert condition_met(profile, {"type": "card_played_count_at_least", "card": "strike", "amount": 5})
assert condition_met(profile, {"type": "potion_used_count_at_least", "potion": "fire_potion", "amount": 2})
assert condition_met(profile, {"type": "timeline_unlocked", "fragment": "first_steps"})
assert not condition_met(profile, {"type": "victories_at_least", "amount": 2})
print("OK")
