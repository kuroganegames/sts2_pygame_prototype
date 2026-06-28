from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.potion_drop_system import PotionDropSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = PotionDropSystem()
run = create_run(registry, "wanderer", seed=2002)

system.set_chance(run, 100)
result = system.roll_drop(run, random.Random(1), node_type="monster", can_receive_potion=True)
assert result.dropped is True
assert result.base_chance_before == 100
assert result.base_chance_after == 90

system.set_chance(run, 0)
result = system.roll_drop(run, random.Random(1), node_type="monster", can_receive_potion=True)
assert result.dropped is False
assert result.base_chance_before == 0
assert result.base_chance_after == 10

system.set_chance(run, -999)
assert system.current_chance(run) == 0
system.set_chance(run, 999)
assert system.current_chance(run) == 100
print("OK")
