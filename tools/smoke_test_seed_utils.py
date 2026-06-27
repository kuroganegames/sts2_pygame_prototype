from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.core.seed_utils import MAX_SEED, random_seed, seed_from_text, stable_string_seed

seed = random_seed()
assert isinstance(seed, int)
assert 0 <= seed < MAX_SEED
assert seed_from_text("12345") == 12345
assert seed_from_text("slime") == stable_string_seed("slime")
assert seed_from_text("slime") == seed_from_text("slime")
assert 0 <= seed_from_text("wanderer-001") < MAX_SEED
print("OK")
