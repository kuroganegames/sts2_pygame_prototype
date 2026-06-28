from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.systems.difficulty_system import DifficultySystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = DifficultySystem(registry)
assert system.max_defined_level() == 10
for level in range(0, 11):
    assert system.level_def(level) is not None
assert "ascender_blight" in registry.cards
print("OK")
