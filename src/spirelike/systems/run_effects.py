from __future__ import annotations

import random
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, RelicInstance, RunState


class RunEffectExecutor:
    """イベント、エンシェント、マップ上の選択肢で使う戦闘外Effect実行器。"""

    def __init__(self, registry: ContentRegistry, rng: random.Random) -> None:
        self.registry = registry
        self.rng = rng

    def execute_many(self, run_state: RunState, effects: list[dict[str, Any]]) -> None:
        for effect in effects or []:
            self.execute(run_state, effect)

    def execute(self, run_state: RunState, effect: dict[str, Any]) -> None:
        effect_type = effect.get("type")
        player = run_state.player
        if effect_type == "heal":
            amount = self.resolve_amount(run_state, effect.get("amount", 0))
            healed = player.heal(amount)
            run_state.add_message(f"HPを{healed}回復")
        elif effect_type == "gain_gold":
            amount = self.resolve_amount(run_state, effect.get("amount", 0))
            player.gold += amount
            run_state.add_message(f"ゴールド +{amount}")
        elif effect_type == "lose_gold":
            amount = min(player.gold, self.resolve_amount(run_state, effect.get("amount", 0)))
            player.gold -= amount
            run_state.add_message(f"ゴールド -{amount}")
        elif effect_type == "gain_relic":
            relic_id = str(effect.get("relic"))
            if relic_id in self.registry.relics and not player.has_relic(relic_id):
                player.relics.append(RelicInstance(relic_id=relic_id))
                run_state.add_message(f"レリック獲得: {self.registry.relic(relic_id).get('name', relic_id)}")
        elif effect_type == "add_card_to_deck":
            card_id = str(effect.get("card"))
            if card_id in self.registry.cards:
                player.deck.append(CardInstance(card_id=card_id, upgraded=bool(effect.get("upgraded", False))))
                run_state.add_message(f"カード追加: {self.registry.card(card_id).get('name', card_id)}")
        elif effect_type == "max_hp":
            amount = self.resolve_amount(run_state, effect.get("amount", 0))
            player.max_hp = max(1, player.max_hp + amount)
            if amount > 0:
                player.hp += amount
            player.hp = min(player.hp, player.max_hp)
            run_state.add_message(f"最大HP {amount:+}")
        elif effect_type == "upgrade_random_card":
            candidates = self._card_candidates(player.deck, effect.get("filter", {}) or {}, require_upgrade=True)
            if candidates:
                card = self.rng.choice(candidates)
                card.upgraded = True
                run_state.add_message(f"カード強化: {self.registry.card_display_name(card.card_id, True)}")
        elif effect_type == "remove_random_card_from_deck":
            candidates = self._card_candidates(player.deck, effect.get("filter", {}) or {}, require_upgrade=False)
            if candidates:
                card = self.rng.choice(candidates)
                player.deck.remove(card)
                run_state.add_message(f"カード削除: {self.registry.card_display_name(card.card_id, card.upgraded)}")
        elif effect_type == "gain_potion":
            from spirelike.systems.potion_system import PotionSystem

            potion_id = str(effect.get("potion"))
            PotionSystem(self.registry).grant_potion(run_state, potion_id)
        elif effect_type == "gain_random_potion":
            from spirelike.systems.potion_system import PotionSystem

            PotionSystem(self.registry).grant_random_potion(
                run_state,
                self.rng,
                rarity_weights=effect.get("rarity_weights"),
            )
        elif effect_type == "none" or effect_type is None:
            return
        else:
            run_state.add_message(f"未実装Effect: {effect_type}")

    def _card_candidates(
        self,
        deck: list[CardInstance],
        filter_def: dict[str, Any],
        *,
        require_upgrade: bool,
    ) -> list[CardInstance]:
        candidates: list[CardInstance] = []
        for card in deck:
            card_def = self.registry.card(card.card_id)
            if require_upgrade and (card.upgraded or not card_def.get("upgrade")):
                continue
            if filter_def.get("type") and card_def.get("type") != filter_def["type"]:
                continue
            if filter_def.get("rarity") and card_def.get("rarity") != filter_def["rarity"]:
                continue
            if filter_def.get("card") and card.card_id != filter_def["card"]:
                continue
            candidates.append(card)
        return candidates

    def resolve_amount(self, run_state: RunState, value: Any) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return 0
        if isinstance(value, dict):
            if value.get("type") == "percent_max_hp":
                return int(run_state.player.max_hp * float(value.get("percent", 0)) / 100)
        return 0
