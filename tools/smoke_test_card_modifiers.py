from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.models.entities import CardInstance
from spirelike.systems.card_modifier_system import CardModifierSystem
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
assert registry.card_modifiers
system = CardModifierSystem(registry)

attack = CardInstance("strike")
skill = CardInstance("guard")
assert system.apply_modifier(attack, "sharp")
assert not system.apply_modifier(skill, "sharp")
assert system.apply_modifier(attack, "sharp")
sharp = system.find_modifier(attack, "sharp")
assert sharp is not None and sharp.stacks == 2

run = create_run(registry, "wanderer", seed=660)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
heavy_card = CardInstance("strike")
assert system.apply_modifier(heavy_card, "heavy")
assert combat.get_card_cost(heavy_card) == 2
light_card = CardInstance("strike")
assert system.apply_modifier(light_card, "light")
assert combat.get_card_cost(light_card) == 0
print("OK")
