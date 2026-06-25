from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.save.save_system import SaveSystem
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

run = create_run(registry, "wanderer", seed=991)
combat = CombatSystem(registry, run, ["cultist"], RunRng(run.seed).combat)
snapshot = combat.to_snapshot()

with tempfile.TemporaryDirectory() as tmp:
    save_system = SaveSystem(Path(tmp), registry)
    save_system.save_run(
        run,
        current_scene="combat",
        scene_payload={
            "node_id": "L01N00",
            "node_type": "monster",
            "enemy_ids": ["cultist"],
            "combat_snapshot": snapshot,
        },
    )
    loaded_run, scene_name, payload = save_system.load_run()

assert scene_name == "combat"
assert payload["node_id"] == "L01N00"
assert payload["combat_snapshot"]
restored = CombatSystem(registry, loaded_run, payload["enemy_ids"], RunRng(loaded_run.seed).combat, snapshot=payload["combat_snapshot"])
assert restored.state.enemies[0].enemy_id == "cultist"
print("OK")
