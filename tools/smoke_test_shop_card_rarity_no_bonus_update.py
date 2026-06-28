from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.systems.shop_system import ShopSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=1905)
run.flags["card_reward_rare_bonus"] = 12.0
offers = ShopSystem(registry).generate_card_offers(run, RunRng(run.seed).shop, count=5)
assert offers
assert run.flags["card_reward_rare_bonus"] == 12.0
for offer in offers:
    assert registry.card(offer.card_id).get("character") in {"wanderer", "neutral"}
print("OK")
