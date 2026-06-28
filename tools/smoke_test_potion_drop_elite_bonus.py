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
run = create_run(registry, "wanderer", seed=2003)
system = PotionDropSystem()
system.set_chance(run, 0)
result = system.roll_drop(run, random.Random(1), node_type="elite", can_receive_potion=True)
assert result.room_bonus == 12.5
assert result.effective_chance == 12.5
assert result.dropped is False

system.set_chance(run, 0)
result = system.roll_drop(run, random.Random(123), node_type="elite", can_receive_potion=True)
assert result.roll < 12.5
assert result.dropped is True
assert result.base_chance_after == 0
print("OK")
