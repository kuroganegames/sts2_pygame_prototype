from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.card_reward_rarity_system import CardRewardRaritySystem
from spirelike.systems.difficulty_system import DifficultySystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
difficulty = DifficultySystem(registry)
card_rewards = CardRewardRaritySystem(registry)

run6 = create_run(registry, "wanderer", seed=2306, run_config={"seed": 2306, "difficulty_level": 6})
assert not difficulty.depletion_enabled(run6)
assert not card_rewards.depletion_enabled(run6)

run7 = create_run(registry, "wanderer", seed=2307, run_config={"seed": 2307, "difficulty_level": 7})
assert difficulty.depletion_enabled(run7)
assert card_rewards.depletion_enabled(run7)
print("OK")
