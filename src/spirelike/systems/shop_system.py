from __future__ import annotations

import random
from dataclasses import dataclass

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import RunState
from spirelike.systems.reward_system import RewardSystem


@dataclass
class ShopOffer:
    card_id: str
    price: int
    sold: bool = False


class ShopSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry
        self.rewards = RewardSystem(registry)

    def generate_card_offers(self, run_state: RunState, rng: random.Random, count: int = 5) -> list[ShopOffer]:
        card_ids = self.rewards.card_choices(run_state, rng, choices=count)
        offers = []
        for card_id in card_ids:
            rarity = self.registry.card(card_id).get("rarity", "common")
            lo, hi = {
                "common": (45, 60),
                "uncommon": (70, 95),
                "rare": (130, 170),
            }.get(rarity, (50, 80))
            offers.append(ShopOffer(card_id=card_id, price=rng.randint(lo, hi)))
        return offers
