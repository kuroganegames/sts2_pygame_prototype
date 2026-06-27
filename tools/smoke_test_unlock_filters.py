from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.content.loader import ContentLoader
from spirelike.core.rng import RunRng
from spirelike.core.run_factory import create_run
from spirelike.profile.profile_data import ProfileState
from spirelike.systems.potion_system import PotionSystem
from spirelike.systems.reward_system import RewardSystem
from spirelike.systems.unlock_system import UnlockSystem

registry = ContentLoader(ROOT / "content").load()
assert not registry.warnings, registry.warnings
profile = ProfileState()
profile.ensure_defaults()
unlocks = UnlockSystem(registry)
unlocks.ensure_initial_unlocks(profile)
run = create_run(registry, "wanderer", seed=1500)
run.flags["unlocked_content"] = unlocks.build_unlocked_snapshot(profile)

# ruleなしのカード/レリック/ポーションは通常通り候補に残る。
reward = RewardSystem(registry)
assert reward.card_choices(run, RunRng(run.seed).reward, choices=1)
assert PotionSystem(registry).random_potion(RunRng(run.seed).reward, run_state=run) in set(run.flags["unlocked_content"]["potions"])

# Run Modifier snapshotではstronger_enemiesが未解放、potion_beltが初期解放。
assert "potion_belt" in run.flags["unlocked_content"]["run_modifiers"]
assert "stronger_enemies" not in run.flags["unlocked_content"]["run_modifiers"]
print("OK")
