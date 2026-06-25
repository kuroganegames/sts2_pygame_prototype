from __future__ import annotations

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, CombatState, RunState
from spirelike.models.selection import CardSelectionCandidate, CardSelectionRequest, CardSelectionResult


class CardSelectionSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def collect_candidates(
        self,
        run_state: RunState,
        request: CardSelectionRequest,
        combat_state: CombatState | None = None,
    ) -> list[CardSelectionCandidate]:
        results: list[CardSelectionCandidate] = []
        for zone in request.source_zones:
            for card in self.zone_cards(run_state, zone, combat_state):
                if self.matches_filter(card, request.filter):
                    results.append(CardSelectionCandidate(zone=zone, card=card))
        return results

    def zone_cards(
        self,
        run_state: RunState,
        zone: str,
        combat_state: CombatState | None = None,
    ) -> list[CardInstance]:
        if zone == "master_deck":
            return run_state.player.deck
        if combat_state is None:
            return []
        if not hasattr(combat_state, zone):
            return []
        return list(getattr(combat_state, zone) or [])

    def find_card_by_instance_id(
        self,
        run_state: RunState,
        instance_id: str,
        zones: list[str],
        combat_state: CombatState | None = None,
    ) -> tuple[str, CardInstance] | None:
        for zone in zones:
            for card in self.zone_cards(run_state, zone, combat_state):
                if card.instance_id == instance_id:
                    return zone, card
        return None

    def validate_result(
        self,
        request: CardSelectionRequest,
        result: CardSelectionResult,
    ) -> tuple[bool, str]:
        if result.skipped:
            if request.allow_skip:
                return True, ""
            return False, "スキップできません"

        count = len(result.selected_instance_ids)
        if request.exact_count is not None and count != request.exact_count:
            return False, f"{request.exact_count}枚選択してください"
        if count < request.min_count:
            return False, f"{request.min_count}枚以上選択してください"
        if count > request.max_count:
            return False, f"{request.max_count}枚まで選択できます"
        return True, ""

    def matches_filter(self, card: CardInstance, filter_def: dict) -> bool:
        filter_def = filter_def or {}
        card_def = self.registry.card(card.card_id)

        types = filter_def.get("types")
        if types is None and filter_def.get("type"):
            types = [filter_def["type"]]
        if types and card_def.get("type") not in types:
            return False

        rarities = filter_def.get("rarities")
        if rarities is None and filter_def.get("rarity"):
            rarities = [filter_def["rarity"]]
        if rarities and card_def.get("rarity") not in rarities:
            return False

        tags = set(card_def.get("tags", []) or [])
        if filter_def.get("tags") and not set(filter_def["tags"]).issubset(tags):
            return False

        if filter_def.get("exclude_tags") and set(filter_def["exclude_tags"]) & tags:
            return False

        if filter_def.get("can_upgrade"):
            if card.upgraded or not card_def.get("upgrade"):
                return False

        if "upgraded" in filter_def and bool(card.upgraded) != bool(filter_def["upgraded"]):
            return False

        if filter_def.get("include_card_ids") and card.card_id not in filter_def["include_card_ids"]:
            return False

        if filter_def.get("exclude_card_ids") and card.card_id in filter_def["exclude_card_ids"]:
            return False

        if filter_def.get("allow_basic") is False and card_def.get("rarity") == "basic":
            return False

        if filter_def.get("allow_status") is False and card_def.get("type") == "status":
            return False

        if filter_def.get("allow_curse") is False and card_def.get("type") == "curse":
            return False

        return True
