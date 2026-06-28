from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.difficulty_system import DifficultySystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = DifficultySystem(registry)

run9 = create_run(registry, "wanderer", seed=2509, run_config={"seed": 2509, "difficulty_level": 9})
assert not system.double_boss_enabled(run9, 3)
assert not run9.flags.get("double_boss_enabled", False)

run10 = create_run(registry, "wanderer", seed=2510, run_config={"seed": 2510, "difficulty_level": 10})
assert system.double_boss_enabled(run10, 3)
assert run10.flags["double_boss_enabled"] is True
print("OK")
