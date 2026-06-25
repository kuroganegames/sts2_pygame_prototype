from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from spirelike.models.entities import CardInstance


@dataclass
class DamageAction:
    source: object
    target: object
    amount: int
    card_def: dict[str, Any]
    name: str = "damage"

    def execute(self, combat: "CombatSystem") -> None:
        if self.target is None:
            return
        if hasattr(self.target, "is_alive") and not self.target.is_alive():
            return
        combat.deal_damage(self.source, self.target, self.amount, self.card_def)
        combat._remove_dead_enemies()
        combat._check_victory_or_defeat()


@dataclass
class GainBlockAction:
    target: object
    amount: int
    name: str = "gain_block"

    def execute(self, combat: "CombatSystem") -> None:
        if self.target is None or self.amount <= 0:
            return
        self.target.block += self.amount
        actor_name = getattr(self.target, "name", "プレイヤー")
        combat.log(f"{actor_name}: ブロック +{self.amount}")


@dataclass
class DrawCardsAction:
    amount: int
    name: str = "draw_cards"

    def execute(self, combat: "CombatSystem") -> None:
        combat.draw_cards_immediate(self.amount)


@dataclass
class GainEnergyAction:
    amount: int
    name: str = "gain_energy"

    def execute(self, combat: "CombatSystem") -> None:
        if self.amount == 0:
            return
        combat.state.energy += self.amount
        combat.log(f"エナジー {self.amount:+}")


@dataclass
class HealAction:
    amount: int
    name: str = "heal"

    def execute(self, combat: "CombatSystem") -> None:
        healed = combat.run_state.player.heal(self.amount)
        combat.log(f"HPを{healed}回復")


@dataclass
class ApplyStatusAction:
    target: object
    status_id: str
    stacks: int
    name: str = "apply_status"

    def execute(self, combat: "CombatSystem") -> None:
        combat.apply_status(self.target, self.status_id, self.stacks)


@dataclass
class AddCardToPileAction:
    card_id: str
    amount: int
    pile: str
    name: str = "add_card_to_pile"

    def execute(self, combat: "CombatSystem") -> None:
        combat.add_generated_card_to_pile(self.card_id, self.amount, self.pile)


@dataclass
class TriggerEventAction:
    event_name: str
    context: dict[str, Any]
    name: str = "trigger_event"

    def execute(self, combat: "CombatSystem") -> None:
        combat.fire_trigger_event(self.event_name, self.context)


@dataclass
class PlayCardAction:
    card: CardInstance
    target: object | None
    spent_energy: int
    name: str = "play_card"

    def execute(self, combat: "CombatSystem") -> None:
        combat.resolve_card_play_immediate(self.card, self.target, self.spent_energy)


@dataclass
class FinishCardUseAction:
    card: CardInstance
    context: dict[str, Any]
    name: str = "finish_card_use"

    def execute(self, combat: "CombatSystem") -> None:
        if self.card not in combat.state.limbo:
            return
        card_def = combat.registry.card(self.card.card_id)

        if card_def.get("type") == "power":
            combat.power_system.add_power_from_card(combat, self.card)
            combat.remove_from_limbo(self.card)
            combat.enqueue_action(
                TriggerEventAction(
                    "power_added",
                    {**self.context, "card": self.card, "card_def": card_def},
                )
            )
            return

        if combat.card_rules.should_exhaust_after_play(self.card):
            combat.move_card(self.card, "limbo", "exhaust_pile")
            combat.enqueue_action(TriggerEventAction("card_exhausted", self.context))
            return

        combat.move_card(self.card, "limbo", "discard_pile")


@dataclass
class EndTurnHandCleanupAction:
    name: str = "end_turn_hand_cleanup"

    def execute(self, combat: "CombatSystem") -> None:
        for card in list(combat.state.hand):
            card_def = combat.registry.card(card.card_id)
            context = {
                "source": combat.run_state.player,
                "target": combat.run_state.player,
                "card": card,
                "card_def": card_def,
            }

            if combat.card_rules.should_exhaust_at_turn_end(card):
                combat.move_card(card, "hand", "exhaust_pile")
                combat.enqueue_action(TriggerEventAction("card_exhausted", context))
                combat.log(f"{combat.registry.card_display_name(card.card_id, card.upgraded)} は消えた")
                continue

            if combat.card_rules.should_retain_at_turn_end(card):
                combat.enqueue_action(TriggerEventAction("card_retained", context))
                continue

            combat.move_card(card, "hand", "discard_pile")
            combat.enqueue_action(TriggerEventAction("card_discarded", context))
