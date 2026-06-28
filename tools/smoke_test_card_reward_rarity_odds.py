from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.card_reward_rarity_system import CardRewardRaritySystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = CardRewardRaritySystem(registry)
run = create_run(registry, "wanderer", seed=1901)

monster = system.rarity_odds(run, "monster")
assert monster.common == 65.0
assert monster.uncommon == 35.0
assert monster.rare == 0.0

elite = system.rarity_odds(run, "elite")
assert elite.common == 55.0
assert elite.uncommon == 40.0
assert elite.rare == 5.0

boss = system.rarity_odds(run, "boss")
assert boss.common == 0.0
assert boss.uncommon == 0.0
assert boss.rare == 100.0
print("OK")
