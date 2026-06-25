from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.profile.profile_system import ProfileSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings

with tempfile.TemporaryDirectory() as tmp:
    profile_system = ProfileSystem(Path(tmp), registry)
    profile_system.profile.summary["runs_started"] = 3
    profile_system.profile.bestiary["slime_small"] = {"seen": True, "encountered": 2, "defeated": 1}
    profile_system.save()
    loaded = ProfileSystem(Path(tmp), registry)

assert loaded.profile.summary["runs_started"] == 3
assert loaded.profile.bestiary["slime_small"]["defeated"] == 1
print("OK")
