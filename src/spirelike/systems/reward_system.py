from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, RelicInstance, RunState
from spirelike.profile.run_metrics import RunMetricsSystem
from spirelike.systems.card_reward_rarity_system import (
    CardRewardContext,
    CardRewardRaritySystem,
    RewardCardChoice,
    normalize_reward_card_choice,
)
from spirelike.systems.potion_drop_system import PotionDropSystem
from spirelike.systems.potion_system import PotionSystem
from spirelike.systems.unlock_system import UnlockSystem


@dataclass
class RewardBundle:
    title: str = "報酬"
    gold: int = 0
    card_choices: list[RewardCardChoice | dict[str, Any] | str] = field(default_factory=list)
    relic_id: str | None = None
    potion_id: str | None = None
    message: str = ""
    base_applied: bool = False
    potion_drop: dict[str, Any] = field(default_factory=dict)


class RewardSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry
        self.potions = PotionSystem(registry)
        self.unlocks = UnlockSystem(registry)
        self.card_rewards = CardRewardRaritySystem(registry)
        self.potion_drops = PotionDropSystem()

    def combat_reward(self, run_state: RunState, node_type: str, rng: random.Random) -> RewardBundle:
        if node_type == "elite":
            gold = rng.randint(25, 40)
            relic = self.random_relic(run_state, rng, allow_boss=False)
            title = "エリート撃破報酬"
            source = "elite"
        elif node_type == "boss":
            gold = rng.randint(90, 120)
            relic = self.random_relic(run_state, rng, allow_boss=True)
            title = "ボス撃破報酬"
            source = "boss"
        else:
            gold = rng.randint(10, 22)
            relic = None
            title = "戦闘報酬"
            source = "monster"
        cards = self.card_choices(run_state, rng, choices=3, source=source, force_rare=(source == "boss"))
        potion = None
        drop_result = self.potion_drops.roll_drop(
            run_state,
            rng,
            node_type=node_type,
            can_receive_potion=self.potions.has_empty_slot(run_state),
        )
        if drop_result.dropped:
            potion = self.potions.random_potion(rng, run_state=run_state)
        return RewardBundle(
            title=title,
            gold=gold,
            card_choices=cards,
            relic_id=relic,
            potion_id=potion,
            potion_drop=drop_result.to_dict(),
        )

    def treasure_reward(self, run_state: RunState, rng: random.Random) -> RewardBundle:
        relic = self.random_relic(run_state, rng, allow_boss=False)
        gold = rng.randint(20, 45)
        potion = self.potions.random_potion(rng, run_state=run_state) if self.potions.has_empty_slot(run_state) else None
        return RewardBundle(title="宝箱", gold=gold, relic_id=relic, potion_id=potion, message="宝箱から報酬を得た。")

    def card_choices(
        self,
        run_state: RunState,
        rng: random.Random,
        *,
        choices: int,
        force_rare: bool = False,
        source: str = "monster",
    ) -> list[RewardCardChoice]:
        return self.card_rewards.card_choices(
            run_state,
            rng,
            CardRewardContext(
                source=source,
                choices=choices,
                force_rare=force_rare,
                update_rare_bonus=(source != "shop"),
                reset_on_rare=(source != "shop"),
                allow_upgrades=(source != "shop"),
            ),
        )

    def random_relic(self, run_state: RunState, rng: random.Random, *, allow_boss: bool) -> str | None:
        owned = {relic.relic_id for relic in run_state.player.relics}
        candidates = []
        for relic_id, item in self.registry.relics.items():
            rarity = item.data.get("rarity", "common")
            if not self.unlocks.run_has_unlocked(run_state, "relics", relic_id):
                continue
            if relic_id in owned and item.data.get("unique", True):
                continue
            if rarity == "starter":
                continue
            if rarity == "boss" and not allow_boss:
                continue
            weight = {"common": 50, "uncommon": 30, "rare": 15, "boss": 10}.get(rarity, 10)
            candidates.append((relic_id, weight))
        if not candidates:
            return None
        return self._weighted_choice(candidates, rng)

    def _weighted_choice(self, weighted: list[tuple[str, float]], rng: random.Random) -> str:
        total = sum(weight for _, weight in weighted)
        roll = rng.uniform(0, total)
        upto = 0.0
        for item_id, weight in weighted:
            upto += weight
            if roll <= upto:
                return item_id
        return weighted[-1][0]

    def apply_base_reward(self, run_state: RunState, reward: RewardBundle) -> None:
        if reward.base_applied:
            return
        if reward.gold:
            run_state.player.gold += reward.gold
            RunMetricsSystem.add_number(run_state, "gold_gained", reward.gold)
            run_state.add_message(f"ゴールド +{reward.gold}")
        if reward.relic_id:
            run_state.player.relics.append(RelicInstance(relic_id=reward.relic_id))
            RunMetricsSystem.record_relic_acquired(run_state, reward.relic_id)
            name = self.registry.relic(reward.relic_id).get("name", reward.relic_id)
            run_state.add_message(f"レリック獲得: {name}")
        if reward.potion_id:
            self.potions.grant_potion(run_state, reward.potion_id)
        reward.base_applied = True

    def choose_card(self, run_state: RunState, choice: RewardCardChoice | dict[str, Any] | str) -> None:
        normalized = normalize_reward_card_choice(choice)
        run_state.player.deck.append(CardInstance(card_id=normalized.card_id, upgraded=normalized.upgraded))
        RunMetricsSystem.record_card_acquired(run_state, normalized.card_id)
        name = self.registry.card_display_name(normalized.card_id, normalized.upgraded)
        run_state.add_message(f"カード追加: {name}")
