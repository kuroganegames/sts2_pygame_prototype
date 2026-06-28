from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.card_reward_rarity_system import CardRewardContext, CardRewardRaritySystem, RARE_BONUS_INITIAL, RARE_BONUS_MAX

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = CardRewardRaritySystem(registry)
run = create_run(registry, "wanderer", seed=1902)

assert system.current_rare_bonus(run) == RARE_BONUS_INITIAL
system._increment_rare_bonus_if_needed(run, CardRewardContext(source="monster"))
assert system.current_rare_bonus(run) == -4.0
system.set_rare_bonus(run, 100)
assert system.current_rare_bonus(run) == RARE_BONUS_MAX
system.set_rare_bonus(run, 10)
rarity = system.roll_rarity(run, random.Random(1), CardRewardContext(source="boss", force_rare=True))
assert rarity == "rare"
assert system.current_rare_bonus(run) == RARE_BONUS_INITIAL

run.flags["run_config"] = {"difficulty_level": 7}
system._increment_rare_bonus_if_needed(run, CardRewardContext(source="monster"))
assert system.current_rare_bonus(run) == -4.5
print("OK")
