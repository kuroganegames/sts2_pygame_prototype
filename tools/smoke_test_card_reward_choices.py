from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.systems.card_reward_rarity_system import reward_choice_card_id
from spirelike.systems.reward_system import RewardSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
reward = RewardSystem(registry)
run = create_run(registry, "wanderer", seed=1903)
choices = reward.card_choices(run, RunRng(run.seed).reward, choices=3, source="monster")
assert choices
for choice in choices:
    card_id = reward_choice_card_id(choice)
    card = registry.card(card_id)
    assert card.get("rarity") not in {"basic"}
    assert card.get("type") not in {"status", "curse"}
    assert card.get("character") in {"wanderer", "neutral"}

boss_choices = reward.card_choices(run, RunRng(run.seed + 1).reward, choices=3, source="boss", force_rare=True)
assert boss_choices
assert run.flags["card_reward_rare_bonus"] == -5.0
print("OK")
