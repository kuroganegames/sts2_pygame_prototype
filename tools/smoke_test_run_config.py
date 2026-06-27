from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.models.run_config import RunConfig, run_config_from_dict, run_config_to_dict

config = RunConfig(
    mode="custom",
    seed=123,
    custom=True,
    selected_modifiers=["rich_start", "stronger_enemies"],
    profile_eligible=False,
    metadata={"seed_text": "abc"},
)
data = run_config_to_dict(config)
restored = run_config_from_dict(data)
assert restored.mode == "custom"
assert restored.seed == 123
assert restored.custom is True
assert restored.profile_eligible is False
assert restored.selected_modifiers == ["rich_start", "stronger_enemies"]
assert run_config_to_dict({"selected_modifiers": ["rich_start"]})["selected_modifiers"] == ["rich_start"]
print("OK")
