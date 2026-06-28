from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.systems.reward_system import RewardSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=2004)
run.flags["potion_drop_chance"] = 100.0
reward = RewardSystem(registry).combat_reward(run, "monster", RunRng(run.seed).reward)
assert reward.potion_id is not None
assert run.flags["potion_drop_chance"] == 90.0
assert reward.potion_drop["dropped"] is True
assert reward.potion_drop["base_chance_before"] == 100.0
assert reward.potion_drop["base_chance_after"] == 90.0
print("OK")
