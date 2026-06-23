from __future__ import annotations

import random


class RunRng:
    """用途別に分けた乱数。処理追加による乱数消費の副作用を減らします。"""

    def __init__(self, seed: int) -> None:
        self.seed = seed
        self.map = random.Random(f"{seed}:map")
        self.combat = random.Random(f"{seed}:combat")
        self.reward = random.Random(f"{seed}:reward")
        self.enemy_ai = random.Random(f"{seed}:enemy_ai")
        self.event = random.Random(f"{seed}:event")
        self.shop = random.Random(f"{seed}:shop")
