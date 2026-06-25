from __future__ import annotations

import random
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, RunState
from spirelike.models.selection import CardSelectionRequest, CardSelectionResult
from spirelike.systems.actions import TriggerEventAction
from spirelike.systems.card_selection_system import CardSelectionSystem


class CardOperationSystem:
    def __init__(self, registry: ContentRegistry, rng: random.Random | None = None) -> None:
        self.registry = registry
        self.selection = CardSelectionSystem(registry)
        self.rng = rng or random.Random()

    def apply_result(
        self,
        run_state: RunState,
        request: CardSelectionRequest,
        result: CardSelectionResult,
        combat=None,
    ) -> None:
        ok, reason = self.selection.validate_result(request, result)
        if not ok:
            run_state.add_message(reason)
            if combat:
                combat.log(reason)
            return
        if result.skipped:
            run_state.add_message("カード選択をスキップ")
            return

        operation_type = request.operation.get("type")
        for instance_id in result.selected_instance_ids:
            found = self.selection.find_card_by_instance_id(
                run_state,
                instance_id,
                request.source_zones,
                combat.state if combat else None,
            )
            if not found:
                continue
            zone, card = found
            if operation_type == "upgrade":
                self.upgrade(run_state, card, combat)
            elif operation_type == "remove":
                self.remove(run_state, zone, card, combat)
            elif operation_type == "transform":
                self.transform(run_state, card, request.operation, combat)
            elif operation_type == "discard":
                self.discard(run_state, zone, card, combat)
            elif operation_type == "exhaust":
                self.exhaust(run_state, zone, card, combat)
            elif operation_type == "fetch_to_hand":
                self.fetch_to_hand(run_state, zone, card, combat)

    def upgrade(self, run_state: RunState, card: CardInstance, combat=None) -> bool:
        card_def = self.registry.card(card.card_id)
        if card.upgraded or not card_def.get("upgrade"):
            return False
        card.upgraded = True
        name = self.registry.card_display_name(card.card_id, True)
        run_state.add_message(f"カード強化: {name}")
        if combat:
            combat.log(f"カード強化: {name}")
        return True

    def remove(self, run_state: RunState, zone: str, card: CardInstance, combat=None) -> bool:
        if zone != "master_deck" or card not in run_state.player.deck:
            return False
        name = self.registry.card_display_name(card.card_id, card.upgraded)
        run_state.player.deck.remove(card)
        run_state.add_message(f"カード削除: {name}")
        return True

    def transform(self, run_state: RunState, card: CardInstance, operation: dict[str, Any], combat=None) -> bool:
        pool_def = operation.get("pool", {}) or {}
        candidates = self._transform_pool(run_state, card, pool_def)
        if not candidates:
            return False
        old_name = self.registry.card_display_name(card.card_id, card.upgraded)
        card.card_id = self.rng.choice(candidates)
        if not pool_def.get("keep_upgrade", False):
            card.upgraded = False
        card.modifiers.clear()
        card.state.clear()
        new_name = self.registry.card_display_name(card.card_id, card.upgraded)
        run_state.add_message(f"カード変化: {old_name} -> {new_name}")
        if combat:
            combat.log(f"カード変化: {old_name} -> {new_name}")
        return True

    def discard(self, run_state: RunState, zone: str, card: CardInstance, combat) -> bool:
        if combat is None or zone == "master_deck" or zone == "discard_pile":
            return False
        moved = combat.move_card(card, zone, "discard_pile")
        if moved:
            context = {
                "source": run_state.player,
                "target": run_state.player,
                "card": card,
                "card_def": self.registry.card(card.card_id),
            }
            combat.enqueue_action(TriggerEventAction("card_discarded", context))
            combat.log(f"{self.registry.card_display_name(card.card_id, card.upgraded)} を捨てた")
        return moved

    def exhaust(self, run_state: RunState, zone: str, card: CardInstance, combat) -> bool:
        if combat is None or zone == "master_deck" or zone == "exhaust_pile":
            return False
        moved = combat.move_card(card, zone, "exhaust_pile")
        if moved:
            context = {
                "source": run_state.player,
                "target": run_state.player,
                "card": card,
                "card_def": self.registry.card(card.card_id),
            }
            combat.enqueue_action(TriggerEventAction("card_exhausted", context))
            combat.log(f"{self.registry.card_display_name(card.card_id, card.upgraded)} を廃棄")
        return moved

    def fetch_to_hand(self, run_state: RunState, zone: str, card: CardInstance, combat) -> bool:
        if combat is None or zone in {"master_deck", "hand"}:
            return False
        if len(combat.state.hand) >= 10:
            combat.log("手札が満杯")
            return False
        moved = combat.move_card(card, zone, "hand")
        if moved:
            combat.log(f"{self.registry.card_display_name(card.card_id, card.upgraded)} を手札へ")
        return moved

    def _transform_pool(self, run_state: RunState, card: CardInstance, pool_def: dict[str, Any]) -> list[str]:
        character_id = run_state.character_id
        candidates: list[str] = []
        for card_id, item in self.registry.cards.items():
            card_def = item.data
            if pool_def.get("exclude_current_card", True) and card_id == card.card_id:
                continue
            if pool_def.get("exclude_basic", True) and card_def.get("rarity") == "basic":
                continue
            if pool_def.get("exclude_status", True) and card_def.get("type") == "status":
                continue
            if pool_def.get("exclude_curse", True) and card_def.get("type") == "curse":
                continue
            card_character = card_def.get("character")
            include_character = pool_def.get("character", True) and card_character == character_id
            include_neutral = pool_def.get("neutral", False) and card_character == "neutral"
            if include_character or include_neutral:
                candidates.append(card_id)
        return candidates
