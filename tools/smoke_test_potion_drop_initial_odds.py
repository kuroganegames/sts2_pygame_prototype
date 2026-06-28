from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.potion_drop_system import INITIAL_POTION_DROP_CHANCE, PotionDropSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=2001)
system = PotionDropSystem()
assert system.current_chance(run) == INITIAL_POTION_DROP_CHANCE
assert system.room_bonus("monster") == 0.0
assert system.room_bonus("elite") == 12.5
assert system.room_bonus("boss") == 0.0
print("OK")
