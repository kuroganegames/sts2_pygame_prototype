from __future__ import annotations

import random
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance, RelicInstance, RunState
from spirelike.models.selection import CardSelectionRequest, CardSelectionResult
from spirelike.systems.card_operation_system import CardOperationSystem
from spirelike.systems.card_selection_system import CardSelectionSystem


SELECTION_RUN_EFFECTS = {
    "upgrade_card": "upgrade",
    "remove_card_from_deck": "remove",
    "transform_card": "transform",
}


class RunEffectExecutor:
    """イベント、エンシェント、マップ上の選択肢で使う戦闘外Effect実行器。"""

    def __init__(self, registry: ContentRegistry, rng: random.Random) -> None:
        self.registry = registry
        self.rng = rng

    def execute_many(self, run_state: RunState, effects: list[dict[str, Any]]) -> bool:
        run_state.pending_selection = None
        run_state.pending_effects = []
        for index, effect in enumerate(effects or []):
            completed = self.execute(run_state, effect, remaining_effects=(effects or [])[index + 1 :])
            if not completed:
                return False
        return True

    def execute(self, run_state: RunState, effect: dict[str, Any], remaining_effects: list[dict[str, Any]] | None = None) -> bool:
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
        elif effect_type in SELECTION_RUN_EFFECTS:
            return self._selection_operation(run_state, effect, SELECTION_RUN_EFFECTS[effect_type], remaining_effects or [])
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
            return True
        else:
            run_state.add_message(f"未実装Effect: {effect_type}")
        return True

    def _selection_operation(
        self,
        run_state: RunState,
        effect: dict[str, Any],
        operation_type: str,
        remaining_effects: list[dict[str, Any]],
    ) -> bool:
        selector = effect.get("selector", {}) or {}
        zones = selector.get("zones") or selector.get("zone") or ["master_deck"]
        if isinstance(zones, str):
            zones = [zones]
        count = int(selector.get("count", effect.get("count", 1)))
        operation = {
            "type": operation_type,
            **{k: v for k, v in effect.items() if k not in {"type", "selector", "title", "message"}},
        }
        request = CardSelectionRequest(
            title=str(effect.get("title", self._default_title(operation_type))),
            message=str(effect.get("message", self._default_message(operation_type))),
            source_zones=list(zones),
            exact_count=count,
            min_count=count,
            max_count=count,
            allow_skip=bool(selector.get("allow_skip", effect.get("allow_skip", False))),
            filter=selector.get("filter", {}) or {},
            operation=operation,
        )

        if selector.get("player_choice", False):
            run_state.pending_selection = request
            run_state.pending_effects = list(remaining_effects or [])
            run_state.add_message(request.message)
            return False

        candidates = CardSelectionSystem(self.registry).collect_candidates(run_state, request, None)
        if not candidates:
            return True
        selected = self.rng.sample(candidates, k=min(count, len(candidates)))
        result = CardSelectionResult(
            request_id=request.request_id,
            selected_instance_ids=[candidate.card.instance_id for candidate in selected],
        )
        CardOperationSystem(self.registry, self.rng).apply_result(run_state, request, result, combat=None)
        return True

    def _default_title(self, operation_type: str) -> str:
        return {
            "upgrade": "カード強化",
            "remove": "カード削除",
            "transform": "カード変化",
        }.get(operation_type, "カード選択")

    def _default_message(self, operation_type: str) -> str:
        return {
            "upgrade": "強化するカードを選んでください。",
            "remove": "削除するカードを選んでください。",
            "transform": "変化させるカードを選んでください。",
        }.get(operation_type, "カードを選んでください。")

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
