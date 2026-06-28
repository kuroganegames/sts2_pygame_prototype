from __future__ import annotations

import random
from dataclasses import dataclass

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import RunState
from spirelike.systems.card_reward_rarity_system import CardRewardContext, CardRewardRaritySystem, reward_choice_card_id
from spirelike.systems.difficulty_system import DifficultySystem
from spirelike.systems.potion_system import PotionSystem
from spirelike.systems.unlock_system import UnlockSystem


@dataclass
class ShopOffer:
    card_id: str
    price: int
    sold: bool = False


@dataclass
class PotionOffer:
    potion_id: str
    price: int
    sold: bool = False


class ShopSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry
        self.card_rewards = CardRewardRaritySystem(registry)
        self.potions = PotionSystem(registry)
        self.unlocks = UnlockSystem(registry)
        self.difficulty = DifficultySystem(registry)

    def card_remove_cost(self, run_state: RunState) -> int:
        removes = int(run_state.flags.get("shop_card_removes", 0))
        config = self.difficulty.card_remove_cost_config(run_state)
        return int(config.get("base", 75)) + removes * int(config.get("step", 25))

    def record_card_removed(self, run_state: RunState) -> None:
        run_state.flags["shop_card_removes"] = int(run_state.flags.get("shop_card_removes", 0)) + 1

    def generate_card_offers(self, run_state: RunState, rng: random.Random, count: int = 5) -> list[ShopOffer]:
        choices = self.card_rewards.card_choices(
            run_state,
            rng,
            CardRewardContext(
                source="shop",
                choices=count,
                update_rare_bonus=False,
                reset_on_rare=False,
                allow_upgrades=False,
            ),
        )
        offers = []
        for choice in choices:
            card_id = reward_choice_card_id(choice)
            rarity = self.registry.card(card_id).get("rarity", "common")
            lo, hi = {
                "common": (45, 60),
                "uncommon": (70, 95),
                "rare": (130, 170),
            }.get(rarity, (50, 80))
            offers.append(ShopOffer(card_id=card_id, price=rng.randint(lo, hi)))
        return offers

    def generate_potion_offers(self, run_state: RunState, rng: random.Random, count: int = 3) -> list[PotionOffer]:
        potion_ids = self.unlocks.filter_run_ids(run_state, "potions", self.registry.potions.keys())
        rng.shuffle(potion_ids)
        offers: list[PotionOffer] = []
        for potion_id in potion_ids[:count]:
            rarity = self.registry.potion(potion_id).get("rarity", "common")
            lo, hi = {
                "common": (35, 55),
                "uncommon": (60, 85),
                "rare": (90, 125),
            }.get(rarity, (45, 80))
            offers.append(PotionOffer(potion_id=potion_id, price=rng.randint(lo, hi)))
        return offers
