from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.systems.difficulty_system import DifficultySystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = DifficultySystem(registry)
levels = system.all_levels()
assert levels
assert levels[0]["level"] == 0
assert [level["level"] for level in levels] == sorted(level["level"] for level in levels)
assert system.max_defined_level() >= 5
assert system.level_def(0)["id"] == "difficulty_00"
print("OK")
