from __future__ import annotations

import random
from dataclasses import dataclass, field

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, RelicInstance, RunState
from spirelike.profile.run_metrics import RunMetricsSystem
from spirelike.systems.potion_system import PotionSystem


@dataclass
class RewardBundle:
    title: str = "報酬"
    gold: int = 0
    card_choices: list[str] = field(default_factory=list)
    relic_id: str | None = None
    potion_id: str | None = None
    message: str = ""
    # セーブ/ロード時にRewardSceneで二重付与しないためのフラグ。
    base_applied: bool = False


class RewardSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry
        self.potions = PotionSystem(registry)

    def combat_reward(self, run_state: RunState, node_type: str, rng: random.Random) -> RewardBundle:
        if node_type == "elite":
            gold = rng.randint(25, 40)
            relic = self.random_relic(run_state, rng, allow_boss=False)
            potion_chance = 0.35
            title = "エリート撃破報酬"
        elif node_type == "boss":
            gold = rng.randint(90, 120)
            relic = self.random_relic(run_state, rng, allow_boss=True)
            potion_chance = 0.50
            title = "ボス撃破報酬"
        else:
            gold = rng.randint(10, 22)
            relic = None
            potion_chance = 0.25
            title = "戦闘報酬"
        cards = self.card_choices(run_state, rng, choices=3, force_rare=(node_type == "boss"))
        potion = None
        if self.potions.has_empty_slot(run_state) and rng.random() < potion_chance:
            potion = self.potions.random_potion(rng)
        return RewardBundle(title=title, gold=gold, card_choices=cards, relic_id=relic, potion_id=potion)

    def treasure_reward(self, run_state: RunState, rng: random.Random) -> RewardBundle:
        relic = self.random_relic(run_state, rng, allow_boss=False)
        gold = rng.randint(20, 45)
        potion = self.potions.random_potion(rng) if self.potions.has_empty_slot(run_state) else None
        return RewardBundle(title="宝箱", gold=gold, relic_id=relic, potion_id=potion, message="宝箱から報酬を得た。")

    def card_choices(
        self,
        run_state: RunState,
        rng: random.Random,
        *,
        choices: int,
        force_rare: bool = False,
    ) -> list[str]:
        character_id = run_state.character_id
        pool = []
        for card_id, item in self.registry.cards.items():
            card = item.data
            rarity = card.get("rarity", "common")
            card_type = card.get("type")
            if rarity == "basic" or card_type in {"status", "curse"}:
                continue
            if card.get("character") not in {character_id, "neutral"}:
                continue
            if force_rare and rarity != "rare":
                continue
            weight = {"common": 65, "uncommon": 30, "rare": 5}.get(rarity, 10)
            if force_rare:
                weight = 1
            pool.append((card_id, weight))
        if not pool:
            return []
        selected: list[str] = []
        attempts = 0
        while len(selected) < choices and attempts < 100:
            attempts += 1
            card_id = self._weighted_choice(pool, rng)
            if card_id not in selected:
                selected.append(card_id)
        return selected

    def random_relic(self, run_state: RunState, rng: random.Random, *, allow_boss: bool) -> str | None:
        owned = {relic.relic_id for relic in run_state.player.relics}
        candidates = []
        for relic_id, item in self.registry.relics.items():
            rarity = item.data.get("rarity", "common")
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

    def choose_card(self, run_state: RunState, card_id: str) -> None:
        run_state.player.deck.append(CardInstance(card_id=card_id))
        RunMetricsSystem.record_card_acquired(run_state, card_id)
        run_state.add_message(f"カード追加: {self.registry.card(card_id).get('name', card_id)}")
