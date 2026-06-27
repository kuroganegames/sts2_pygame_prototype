from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
assert registry.unlock_rules
rule = registry.unlock_rule("unlock_stronger_enemies")
assert rule["target_type"] == "run_modifier"
assert rule["target_id"] == "stronger_enemies"
assert rule["conditions"][0]["type"] == "victories_at_least"
print("OK")
