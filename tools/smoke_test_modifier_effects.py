from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.models.entities import CardInstance
from spirelike.models.selection import CardSelectionResult
from spirelike.systems.combat_system import CombatSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

run = create_run(registry, "wanderer", seed=664)
combat = CombatSystem(registry, run, ["slime_small"], RunRng(run.seed).combat)
card = CardInstance("strike")
combat.state.hand = [card]
effects = [
    {
        "type": "apply_card_modifier",
        "modifier": "heavy",
        "selector": {"zones": ["hand"], "count": 1, "mode": "random"},
    }
]
combat.executor.execute_many(effects, {"source": run.player, "target": run.player, "card_def": {}})
combat.resolve_actions()
assert any(mod.modifier_id == "heavy" for mod in card.modifiers)

combat.executor.execute_many(
    [
        {
            "type": "cleanse_card_modifiers",
            "modifier_type": "affliction",
            "selector": {"zones": ["hand"], "count": 1, "mode": "random"},
        }
    ],
    {"source": run.player, "target": run.player, "card_def": {}},
)
combat.resolve_actions()
assert not card.modifiers

combat.executor.execute_many(
    [
        {
            "type": "apply_card_modifier",
            "modifier": "sharp",
            "selector": {"zones": ["hand"], "count": 1, "player_choice": True},
        }
    ],
    {"source": run.player, "target": run.player, "card_def": {}},
)
combat.resolve_actions()
assert combat.state.pending_selection is not None
req = combat.state.pending_selection
combat.complete_card_selection(CardSelectionResult(req.request_id, [card.instance_id]))
assert any(mod.modifier_id == "sharp" for mod in card.modifiers)
print("OK")
