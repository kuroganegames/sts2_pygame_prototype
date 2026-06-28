from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.profile.profile_data import ProfileState
from spirelike.systems.unlock_tree_system import UnlockTreeSystem
from spirelike.systems.unlock_system import UnlockSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
profile = ProfileState()
profile.ensure_defaults()
UnlockSystem(registry).ensure_initial_unlocks(profile)

system = UnlockTreeSystem(registry)
nodes = system.nodes(profile)
assert nodes
assert any(node.unlock_id == "unlock_focus_blade" for node in nodes)
assert nodes == sorted(nodes, key=lambda node: (node.tier, node.order, node.unlock_id))
card_nodes = system.nodes(profile, "card")
assert card_nodes and all(node.category == "card" for node in card_nodes)
focus = next(node for node in card_nodes if node.unlock_id == "unlock_focus_blade")
assert not focus.unlocked
assert focus.condition_lines
print("OK")
