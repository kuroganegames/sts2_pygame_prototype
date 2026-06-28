from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import RunState
from spirelike.systems.unlock_system import UnlockSystem

RARE_BONUS_INITIAL = -5.0
RARE_BONUS_MAX = 40.0


@dataclass(frozen=True)
class CardRewardRarityOdds:
    common: float
    uncommon: float
    rare: float


@dataclass(frozen=True)
class CardRewardContext:
    source: str
    choices: int = 3
    force_rare: bool = False
    update_rare_bonus: bool = True
    reset_on_rare: bool = True
    allow_upgrades: bool = True


@dataclass
class RewardCardChoice:
    card_id: str
    upgraded: bool = False
    rarity: str = "common"


BASE_ODDS = {
    "monster": CardRewardRarityOdds(common=60.0, uncommon=37.0, rare=3.0),
    "elite": CardRewardRarityOdds(common=50.0, uncommon=40.0, rare=10.0),
    "boss": CardRewardRarityOdds(common=0.0, uncommon=0.0, rare=100.0),
    "shop": CardRewardRarityOdds(common=54.0, uncommon=37.0, rare=9.0),
}

FALLBACK_RARITIES = {
    "rare": ["rare", "uncommon", "common"],
    "uncommon": ["uncommon", "common", "rare"],
    "common": ["common", "uncommon", "rare"],
}


def normalize_reward_card_choice(choice: RewardCardChoice | dict[str, Any] | str) -> RewardCardChoice:
    if isinstance(choice, RewardCardChoice):
        return choice
    if isinstance(choice, str):
        return RewardCardChoice(card_id=choice, upgraded=False, rarity="")
    return RewardCardChoice(
        card_id=str(choice.get("card_id")),
        upgraded=bool(choice.get("upgraded", False)),
        rarity=str(choice.get("rarity", "")),
    )


def reward_choice_card_id(choice: RewardCardChoice | dict[str, Any] | str) -> str:
    return normalize_reward_card_choice(choice).card_id


def reward_choice_upgraded(choice: RewardCardChoice | dict[str, Any] | str) -> bool:
    return normalize_reward_card_choice(choice).upgraded


def reward_choice_to_dict(choice: RewardCardChoice | dict[str, Any] | str) -> dict[str, Any]:
    normalized = normalize_reward_card_choice(choice)
    return {
        "card_id": normalized.card_id,
        "upgraded": bool(normalized.upgraded),
        "rarity": normalized.rarity,
    }


def reward_choice_from_dict(data: dict[str, Any] | str) -> RewardCardChoice:
    return normalize_reward_card_choice(data)


class CardRewardRaritySystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry
        self.unlocks = UnlockSystem(registry)

    def depletion_enabled(self, run_state: RunState) -> bool:
        config = run_state.flags.get("run_config", {}) or {}
        return int(config.get("difficulty_level", 0)) >= 7

    def current_rare_bonus(self, run_state: RunState) -> float:
        return float(run_state.flags.get("card_reward_rare_bonus", RARE_BONUS_INITIAL))

    def set_rare_bonus(self, run_state: RunState, value: float) -> None:
        run_state.flags["card_reward_rare_bonus"] = max(
            RARE_BONUS_INITIAL,
            min(RARE_BONUS_MAX, float(value)),
        )

    def rarity_odds(self, run_state: RunState, source: str) -> CardRewardRarityOdds:
        base = BASE_ODDS.get(source, BASE_ODDS["monster"])
        if source == "boss":
            return base

        base_rare = base.rare * (0.5 if self.depletion_enabled(run_state) else 1.0)
        rare = base_rare + self.current_rare_bonus(run_state)
        uncommon = base.uncommon
        if rare < 0:
            uncommon = max(0.0, uncommon + rare)
            rare = 0.0
        common = max(0.0, 100.0 - rare - uncommon)
        return CardRewardRarityOdds(common=common, uncommon=uncommon, rare=rare)

    def roll_rarity(
        self,
        run_state: RunState,
        rng: random.Random,
        context: CardRewardContext,
    ) -> str:
        if context.force_rare or context.source == "boss":
            if context.update_rare_bonus and context.reset_on_rare:
                self.set_rare_bonus(run_state, RARE_BONUS_INITIAL)
            return "rare"

        odds = self.rarity_odds(run_state, context.source)
        roll = rng.uniform(0, 100)
        if roll < odds.rare:
            if context.update_rare_bonus and context.reset_on_rare:
                self.set_rare_bonus(run_state, RARE_BONUS_INITIAL)
            return "rare"
        if roll < odds.rare + odds.uncommon:
            self._increment_rare_bonus_if_needed(run_state, context)
            return "uncommon"
        self._increment_rare_bonus_if_needed(run_state, context)
        return "common"

    def _increment_rare_bonus_if_needed(self, run_state: RunState, context: CardRewardContext) -> None:
        if not context.update_rare_bonus:
            return
        increment = 0.5 if self.depletion_enabled(run_state) else 1.0
        self.set_rare_bonus(run_state, self.current_rare_bonus(run_state) + increment)

    def card_pool_for_rarity(
        self,
        run_state: RunState,
        rarity: str,
        excluded: set[str] | None = None,
    ) -> list[str]:
        character_id = run_state.character_id
        excluded = excluded or set()
        result: list[str] = []
        for card_id, item in self.registry.cards.items():
            if card_id in excluded:
                continue
            card = item.data
            if card.get("rarity", "common") != rarity:
                continue
            if rarity == "basic" or card.get("type") in {"status", "curse"}:
                continue
            if card.get("character") not in {character_id, "neutral"}:
                continue
            if not self.unlocks.run_has_unlocked(run_state, "cards", card_id):
                continue
            result.append(card_id)
        return result

    def roll_upgraded(
        self,
        run_state: RunState,
        rng: random.Random,
        card_id: str,
        source: str,
        allow_upgrades: bool,
    ) -> bool:
        if not allow_upgrades or source == "shop":
            return False
        card = self.registry.card(card_id)
        if card.get("rarity") == "rare" or not card.get("upgrade"):
            return False
        act = int(getattr(run_state, "act", 1))
        if act <= 1:
            chance = 0.0
        elif act == 2:
            chance = 25.0
        else:
            chance = 50.0
        if self.depletion_enabled(run_state):
            chance *= 0.5
        return rng.uniform(0, 100) < chance

    def roll_card_choice(
        self,
        run_state: RunState,
        rng: random.Random,
        context: CardRewardContext,
        excluded: set[str],
    ) -> RewardCardChoice | None:
        rolled_rarity = self.roll_rarity(run_state, rng, context)
        for rarity in FALLBACK_RARITIES.get(rolled_rarity, [rolled_rarity, "common", "uncommon", "rare"]):
            pool = self.card_pool_for_rarity(run_state, rarity, excluded)
            if not pool:
                continue
            card_id = rng.choice(pool)
            upgraded = self.roll_upgraded(run_state, rng, card_id, context.source, context.allow_upgrades)
            return RewardCardChoice(card_id=card_id, upgraded=upgraded, rarity=rarity)
        return None

    def card_choices(
        self,
        run_state: RunState,
        rng: random.Random,
        context: CardRewardContext,
    ) -> list[RewardCardChoice]:
        selected: list[RewardCardChoice] = []
        excluded: set[str] = set()
        attempts = 0
        while len(selected) < max(0, int(context.choices)) and attempts < 100:
            attempts += 1
            choice = self.roll_card_choice(run_state, rng, context, excluded)
            if choice is None:
                break
            selected.append(choice)
            excluded.add(choice.card_id)
        return selected
