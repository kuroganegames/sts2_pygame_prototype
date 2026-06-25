from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.models.entities import AncientBlessingInstance, PotionInstance, RelicInstance
from spirelike.save.save_system import SaveSystem
from spirelike.systems.card_modifier_system import CardModifierSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

run = create_run(registry, "wanderer", seed=770)
run.player.hp = 42
run.player.gold = 321
run.player.relics.append(RelicInstance("iron_leaf"))
run.player.potions[0] = PotionInstance("fire_potion")
run.ancient_blessings.append(AncientBlessingInstance("old_smith", "battle_temper"))
run.map_state.available_nodes()[0].visited = True
card = run.player.deck[0]
assert CardModifierSystem(registry).apply_modifier(card, "sharp")

with tempfile.TemporaryDirectory() as tmp:
    save_system = SaveSystem(Path(tmp), registry)
    save_system.save_run(run, current_scene="map", scene_payload={})
    loaded, scene_name, payload = save_system.load_run()

assert scene_name == "map"
assert payload["run_state"] is loaded
assert loaded.seed == run.seed
assert loaded.player.hp == 42
assert loaded.player.gold == 321
assert loaded.player.potions[0] is not None and loaded.player.potions[0].potion_id == "fire_potion"
assert any(relic.relic_id == "iron_leaf" for relic in loaded.player.relics)
assert loaded.ancient_blessings and loaded.ancient_blessings[0].ancient_id == "old_smith"
assert loaded.player.deck[0].modifiers and loaded.player.deck[0].modifiers[0].modifier_id == "sharp"
print("OK")
