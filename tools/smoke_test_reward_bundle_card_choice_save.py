from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.save.serializer import reward_bundle_from_dict, reward_bundle_to_dict
from spirelike.systems.card_reward_rarity_system import RewardCardChoice
from spirelike.systems.reward_system import RewardBundle

bundle = RewardBundle(
    title="テスト報酬",
    card_choices=[RewardCardChoice(card_id="strike", upgraded=True, rarity="common")],
)
data = reward_bundle_to_dict(bundle)
assert data["card_choices"] == [{"card_id": "strike", "upgraded": True, "rarity": "common"}]
restored = reward_bundle_from_dict(data)
assert restored.card_choices[0].card_id == "strike"
assert restored.card_choices[0].upgraded is True
assert restored.card_choices[0].rarity == "common"

legacy = reward_bundle_from_dict({"title": "旧", "card_choices": ["defend"]})
assert legacy.card_choices[0].card_id == "defend"
assert legacy.card_choices[0].upgraded is False
print("OK")
