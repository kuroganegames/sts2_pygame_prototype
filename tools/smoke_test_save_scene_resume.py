from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.save.save_system import SaveSystem
from spirelike.systems.reward_system import RewardBundle

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
run = create_run(registry, "wanderer", seed=772)
reward = RewardBundle(
    title="テスト報酬",
    gold=12,
    card_choices=["strike"],
    relic_id="iron_leaf",
    potion_id="fire_potion",
    message="saved reward",
    base_applied=True,
)
scene_payload = SaveSystem.safe_scene_payload(
    "reward",
    {"node_id": "L01N00", "reward": reward, "after_boss": False},
)

with tempfile.TemporaryDirectory() as tmp:
    save_system = SaveSystem(Path(tmp), registry)
    save_system.save_run(run, current_scene="reward", scene_payload=scene_payload)
    loaded, scene_name, payload = save_system.load_run()

assert scene_name == "reward"
assert payload["node_id"] == "L01N00"
assert payload["reward"].title == "テスト報酬"
assert payload["reward"].base_applied is True
assert payload["reward"].card_choices == ["strike"]
assert payload["run_state"] is loaded
print("OK")
