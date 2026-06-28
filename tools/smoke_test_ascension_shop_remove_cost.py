from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.shop_system import ShopSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
shop = ShopSystem(registry)

run5 = create_run(registry, "wanderer", seed=2405, run_config={"seed": 2405, "difficulty_level": 5})
assert shop.card_remove_cost(run5) == 75
shop.record_card_removed(run5)
assert shop.card_remove_cost(run5) == 100

run6 = create_run(registry, "wanderer", seed=2406, run_config={"seed": 2406, "difficulty_level": 6})
assert shop.card_remove_cost(run6) == 100
shop.record_card_removed(run6)
assert shop.card_remove_cost(run6) == 150
print("OK")
