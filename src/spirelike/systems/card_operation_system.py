from __future__ import annotations

import random
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, RunState
from spirelike.models.selection import CardSelectionRequest, CardSelectionResult
from spirelike.profile.run_metrics import RunMetricsSystem
from spirelike.systems.actions import TriggerEventAction
from spirelike.systems.card_modifier_system import CardModifierSystem
from spirelike.systems.card_selection_system import CardSelectionSystem


class CardOperationSystem:
    def __init__(self, registry: ContentRegistry, rng: random.Random | None = None) -> None:
        self.registry = registry
        self.selection = CardSelectionSystem(registry)
        self.card_modifiers = CardModifierSystem(registry)
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
            elif operation_type == "apply_modifier":
                self.apply_modifier(run_state, card, request.operation, combat)
            elif operation_type == "remove_modifier":
                self.remove_modifier(run_state, card, request.operation, combat)
            elif operation_type == "cleanse_modifiers":
                self.cleanse_modifiers(run_state, card, request.operation, combat)

    def upgrade(self, run_state: RunState, card: CardInstance, combat=None) -> bool:
        card_def = self.registry.card(card.card_id)
        if card.upgraded or not card_def.get("upgrade"):
            return False
        card.upgraded = True
        RunMetricsSystem.record_card_upgraded(run_state, card.card_id)
        name = self.registry.card_display_name(card.card_id, True)
        run_state.add_message(f"カード強化: {name}")
        if combat:
            combat.log(f"カード強化: {name}")
        return True

    def remove(self, run_state: RunState, zone: str, card: CardInstance, combat=None) -> bool:
        if zone != "master_deck" or card not in run_state.player.deck:
            return False
        name = self.registry.card_display_name(card.card_id, card.upgraded)
        RunMetricsSystem.record_card_removed(run_state, card.card_id)
        run_state.player.deck.remove(card)
        run_state.add_message(f"カード削除: {name}")
        return True

    def transform(self, run_state: RunState, card: CardInstance, operation: dict[str, Any], combat=None) -> bool:
        pool_def = operation.get("pool", {}) or {}
        candidates = self._transform_pool(run_state, card, pool_def)
        if not candidates:
            return False
        old_card_id = card.card_id
        old_name = self.registry.card_display_name(card.card_id, card.upgraded)
        card.card_id = self.rng.choice(candidates)
        if not pool_def.get("keep_upgrade", False):
            card.upgraded = False
        card.modifiers.clear()
        card.state.clear()
        RunMetricsSystem.record_card_transformed(run_state, old_card_id, card.card_id)
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

    def apply_modifier(self, run_state: RunState, card: CardInstance, operation: dict[str, Any], combat=None) -> bool:
        modifier_id = str(operation.get("modifier"))
        stacks = int(operation.get("stacks", 1))
        duration = operation.get("duration")
        ok = self.card_modifiers.apply_modifier(
            card,
            modifier_id,
            duration_override=duration,
            stacks=stacks,
            source=operation.get("source"),
        )
        if not ok:
            return False
        RunMetricsSystem.record_modifier_applied(run_state, modifier_id)
        modifier_name = self.registry.card_modifier(modifier_id).get("name", modifier_id)
        card_name = self.registry.card_display_name(card.card_id, card.upgraded)
        msg = f"{card_name} に {modifier_name} を付与"
        run_state.add_message(msg)
        if combat:
            combat.log(msg)
        return True

    def remove_modifier(self, run_state: RunState, card: CardInstance, operation: dict[str, Any], combat=None) -> bool:
        modifier_id = str(operation.get("modifier"))
        ok = self.card_modifiers.remove_modifier(card, modifier_id, stacks=operation.get("stacks"))
        if not ok:
            return False
        RunMetricsSystem.record_modifier_cleansed(run_state, modifier_id)
        modifier_name = self.registry.card_modifier(modifier_id).get("name", modifier_id)
        card_name = self.registry.card_display_name(card.card_id, card.upgraded)
        msg = f"{card_name} から {modifier_name} を解除"
        run_state.add_message(msg)
        if combat:
            combat.log(msg)
        return True

    def cleanse_modifiers(self, run_state: RunState, card: CardInstance, operation: dict[str, Any], combat=None) -> bool:
        modifier_type = str(operation.get("modifier_type", "affliction"))
        targets = [m.modifier_id for m in self.card_modifiers.active_modifiers(card) if m.modifier_type == modifier_type]
        removed = self.card_modifiers.remove_by_type(card, modifier_type, count=operation.get("count"))
        if removed <= 0:
            return False
        for modifier_id in targets[:removed]:
            RunMetricsSystem.record_modifier_cleansed(run_state, modifier_id)
        card_name = self.registry.card_display_name(card.card_id, card.upgraded)
        msg = f"{card_name} の {modifier_type} を{removed}個解除"
        run_state.add_message(msg)
        if combat:
            combat.log(msg)
        return True

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
