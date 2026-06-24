from __future__ import annotations

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance


CARD_FLAGS = {"exhaust", "retain", "ethereal", "innate", "unplayable"}


class CardRules:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def has_flag(self, card: CardInstance, flag: str) -> bool:
        if flag in card.state:
            return bool(card.state[flag])

        card_def = self.registry.card(card.card_id)
        upgrade = card_def.get("upgrade", {}) or {}

        if card.upgraded and flag in upgrade:
            return bool(upgrade[flag])

        if flag in card_def:
            return bool(card_def[flag])

        keywords = set(card_def.get("keywords", []) or [])
        if card.upgraded:
            keywords.update(upgrade.get("keywords", []) or [])
        return flag in keywords

    def is_power(self, card: CardInstance) -> bool:
        return self.registry.card(card.card_id).get("type") == "power"

    def should_exhaust_after_play(self, card: CardInstance) -> bool:
        return card.temporary or self.has_flag(card, "exhaust")

    def should_retain_at_turn_end(self, card: CardInstance) -> bool:
        return self.has_flag(card, "retain")

    def should_exhaust_at_turn_end(self, card: CardInstance) -> bool:
        # EtherealはRetainより優先する。
        return self.has_flag(card, "ethereal")
