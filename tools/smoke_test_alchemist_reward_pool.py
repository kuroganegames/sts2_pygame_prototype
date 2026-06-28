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
reward = RewardSystem(registry)

alchemist = create_run(registry, "alchemist", seed=1805)
alchemist_cards = reward.card_choices(alchemist, RunRng(alchemist.seed).reward, choices=20)
assert alchemist_cards
assert all(registry.card(card_id).get("character") in {"alchemist", "neutral"} for card_id in alchemist_cards)

wanderer = create_run(registry, "wanderer", seed=1806)
wanderer_cards = reward.card_choices(wanderer, RunRng(wanderer.seed).reward, choices=20)
assert all(registry.card(card_id).get("character") in {"wanderer", "neutral"} for card_id in wanderer_cards)
assert not any(registry.card(card_id).get("character") == "alchemist" for card_id in wanderer_cards)
print("OK")
