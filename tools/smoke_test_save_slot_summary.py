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

with tempfile.TemporaryDirectory() as tmp:
    save_system = SaveSystem(Path(tmp), registry)
    run1 = create_run(registry, "wanderer", seed=1005)
    run1.floor = 4
    save_system.save_run(run1, current_scene="map", slot_id="slot_001")

    run2 = create_run(registry, "wanderer", seed=1006)
    run2.floor = 2
    combat = CombatSystem(registry, run2, ["slime_small"], RunRng(run2.seed).combat)
    save_system.save_run(
        run2,
        current_scene="combat",
        scene_payload={
            "node_id": "L02N00",
            "node_type": "monster",
            "enemy_ids": ["slime_small"],
            "combat_snapshot": combat.to_snapshot(),
        },
        slot_id="slot_002",
    )

    slots = save_system.list_slots()
    assert slots[0].scene_label == "マップ"
    assert slots[0].floor == 4
    assert slots[0].deck_size == len(run1.player.deck)
    assert slots[1].scene_label == "戦闘中"
    assert slots[1].floor == 2
    assert slots[1].hp == run2.player.hp
print("OK")
