from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.systems.run_modifier_system import RunModifierSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
config = {
    "mode": "custom",
    "seed": 1234,
    "custom": True,
    "selected_modifiers": ["rich_start", "potion_belt", "stronger_enemies"],
    "profile_eligible": False,
}
run = create_run(registry, "wanderer", run_config=config)
assert run.seed == 1234
assert run.flags["run_config"]["selected_modifiers"] == config["selected_modifiers"]
assert run.player.gold >= 199
assert run.player.potion_slots == 4
assert len(run.player.potions) == 4
assert RunModifierSystem(registry).enemy_hp_multiplier(run) == 1.2
print("OK")
