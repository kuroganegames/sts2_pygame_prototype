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

with tempfile.TemporaryDirectory() as tmp:
    profile_system = ProfileSystem(Path(tmp), registry)
    run = create_run(registry, "wanderer", seed=880)
    profile_system.record_run_started(run)
    RunMetricsSystem.record_enemy_defeated(run, "slime_small")
    RunMetricsSystem.record_card_played(run, "strike")
    profile_system.finalize_run(run, "victory")
    profile_system.finalize_run(run, "victory")
    assert profile_system.profile.summary["runs_started"] == 1
    assert profile_system.profile.summary["victories"] == 1
    assert len(profile_system.profile.run_history) == 1
    assert profile_system.profile.run_history[0]["result"] == "victory"
print("OK")
