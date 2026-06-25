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
    run = create_run(registry, "wanderer", seed=881)
    profile_system.record_run_started(run)
    RunMetricsSystem.record_enemy_seen(run, "cultist")
    RunMetricsSystem.record_enemy_defeated(run, "cultist")
    RunMetricsSystem.record_card_acquired(run, "quick_slash")
    RunMetricsSystem.record_card_played(run, "quick_slash")
    RunMetricsSystem.record_potion_acquired(run, "fire_potion")
    RunMetricsSystem.record_potion_used(run, "fire_potion")
    RunMetricsSystem.record_modifier_applied(run, "sharp")
    profile_system.finalize_run(run, "defeat")
    profile = profile_system.profile
    assert profile.bestiary["cultist"]["encountered"] == 1
    assert profile.bestiary["cultist"]["defeated"] == 1
    assert profile.compendium["cards"]["quick_slash"]["played"] == 1
    assert profile.compendium["potions"]["fire_potion"]["used"] == 1
    assert profile.compendium["card_modifiers"]["sharp"]["applied"] == 1
print("OK")
