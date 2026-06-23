from __future__ import annotations

import random
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, RelicInstance, RunState


class RunEffectExecutor:
    """イベントやショップなど、戦闘外で使う簡易Effect実行器。"""

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
            player.max_hp += amount
            player.hp += max(0, amount)
            run_state.add_message(f"最大HP {amount:+}")
        elif effect_type == "upgrade_random_card":
            candidates = [card for card in player.deck if not card.upgraded and self.registry.card(card.card_id).get("upgrade")]
            if candidates:
                card = self.rng.choice(candidates)
                card.upgraded = True
                run_state.add_message(f"カード強化: {self.registry.card_display_name(card.card_id, True)}")

    def resolve_amount(self, run_state: RunState, value: Any) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, dict):
            if value.get("type") == "percent_max_hp":
                return int(run_state.player.max_hp * float(value.get("percent", 0)) / 100)
        return 0
