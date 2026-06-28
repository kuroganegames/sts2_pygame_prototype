from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.difficulty_system import DifficultySystem
from spirelike.systems.reward_system import RewardSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = DifficultySystem(registry)
reward = RewardSystem(registry)

run2 = create_run(registry, "wanderer", seed=2202, run_config={"seed": 2202, "difficulty_level": 2})
assert system.gold_reward_multiplier(run2, "combat") == 1.0

run3 = create_run(registry, "wanderer", seed=2203, run_config={"seed": 2203, "difficulty_level": 3})
assert system.gold_reward_multiplier(run3, "combat") == 0.75
assert system.gold_reward_multiplier(run3, "treasure") == 0.75
assert reward.apply_gold_multiplier(run3, 100, "combat") == 75
print("OK")
