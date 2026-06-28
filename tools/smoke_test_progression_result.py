from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.profile.progression_result import ProgressionResult

result = ProgressionResult()
assert not result.has_anything()
result.new_achievements.append({"id": "first_victory"})
assert result.has_anything()
result = ProgressionResult()
result.new_content_unlocks.append({"target_id": "stronger_enemies"})
assert result.has_anything()
print("OK")
