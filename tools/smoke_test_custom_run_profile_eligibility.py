from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.run_factory import create_run
from spirelike.profile.profile_system import ProfileSystem
from spirelike.profile.run_metrics import RunMetricsSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
config = {
    "mode": "custom",
    "seed": 999,
    "custom": True,
    "selected_modifiers": ["rich_start"],
    "profile_eligible": False,
}
with tempfile.TemporaryDirectory() as tmp:
    profile_system = ProfileSystem(Path(tmp), registry)
    run = create_run(registry, "wanderer", run_config=config)
    profile_system.record_run_started(run)
    RunMetricsSystem.record_enemy_defeated(run, "cultist")
    RunMetricsSystem.record_modifier_applied(run, "sharp")
    profile_system.finalize_run(run, "victory")
    profile = profile_system.profile
    assert len(profile.run_history) == 1
    assert profile.run_history[0]["mode"] == "custom"
    assert profile.run_history[0]["profile_eligible"] is False
    assert profile.summary["victories"] == 0
    assert "cultist" not in profile.bestiary
    assert "sharp" not in profile.compendium["card_modifiers"]
print("OK")
