from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.card_reward_rarity_system import CardRewardRaritySystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
system = CardRewardRaritySystem(registry)
run = create_run(registry, "wanderer", seed=1904)
non_rare = next(card_id for card_id, item in registry.cards.items() if item.data.get("character") == "wanderer" and item.data.get("rarity") in {"common", "uncommon"} and item.data.get("upgrade"))

run.act = 1
assert not system.roll_upgraded(run, random.Random(1), non_rare, "monster", True)
run.act = 2
assert system.roll_upgraded(run, random.Random(1), non_rare, "monster", True)
run.act = 3
assert system.roll_upgraded(run, random.Random(1), non_rare, "monster", True)
assert not system.roll_upgraded(run, random.Random(1), non_rare, "shop", True)

rare_cards = [card_id for card_id, item in registry.cards.items() if item.data.get("character") == "wanderer" and item.data.get("rarity") == "rare"]
if rare_cards:
    assert not system.roll_upgraded(run, random.Random(1), rare_cards[0], "monster", True)

run.flags["run_config"] = {"difficulty_level": 7}
run.act = 2
assert not system.roll_upgraded(run, random.Random(5), non_rare, "monster", True)
print("OK")
