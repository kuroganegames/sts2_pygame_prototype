from __future__ import annotations

import hashlib
import random
import time

MAX_SEED = 2_147_483_647


def random_seed() -> int:
    return int(time.time() * 1000 + random.randint(0, 999_999)) % MAX_SEED


def stable_string_seed(text: str) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % MAX_SEED


def seed_from_text(text: str) -> int:
    text = str(text).strip()
    if not text:
        return random_seed()
    try:
        return int(text) % MAX_SEED
    except ValueError:
        return stable_string_seed(text)
