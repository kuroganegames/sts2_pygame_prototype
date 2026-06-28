from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
assert registry.achievements
assert "first_victory" in registry.achievements
achievement = registry.achievement("first_victory")
assert achievement["conditions"][0]["type"] == "victories_at_least"
print("OK")
