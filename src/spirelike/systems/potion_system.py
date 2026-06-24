from __future__ import annotations

import random
from typing import Optional

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import EnemyInstance, PotionInstance, RunState


class PotionSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def first_empty_slot(self, run_state: RunState) -> int | None:
        return run_state.player.first_empty_potion_slot()

    def has_empty_slot(self, run_state: RunState) -> bool:
        return self.first_empty_slot(run_state) is not None

    def grant_potion(self, run_state: RunState, potion_id: str) -> bool:
        if potion_id not in self.registry.potions:
            run_state.add_message(f"不明なポーション: {potion_id}")
            return False
        slot = self.first_empty_slot(run_state)
        if slot is None:
            run_state.add_message("ポーションスロットが満杯")
            return False
        run_state.player.potions[slot] = PotionInstance(potion_id=potion_id)
        name = self.registry.potion(potion_id).get("name", potion_id)
        run_state.add_message(f"ポーション獲得: {name}")
        return True

    def grant_random_potion(
        self,
        run_state: RunState,
        rng: random.Random,
        rarity_weights: dict[str, int | float] | None = None,
    ) -> str | None:
        potion_id = self.random_potion(rng, rarity_weights=rarity_weights)
        if potion_id and self.grant_potion(run_state, potion_id):
            return potion_id
        return None

    def random_potion(
        self,
        rng: random.Random,
        rarity_weights: dict[str, int | float] | None = None,
    ) -> str | None:
        if not self.registry.potions:
            return None
        rarity_weights = rarity_weights or {"common": 65, "uncommon": 25, "rare": 10}
        candidates: list[tuple[str, float]] = []
        for potion_id, item in self.registry.potions.items():
            rarity = str(item.data.get("rarity", "common"))
            weight = float(rarity_weights.get(rarity, 0))
            if weight > 0:
                candidates.append((potion_id, weight))
        if not candidates:
            candidates = [(potion_id, 1.0) for potion_id in self.registry.potions]
        return self._weighted_choice(candidates, rng)

    def discard_potion(self, run_state: RunState, slot_index: int) -> bool:
        if not 0 <= slot_index < len(run_state.player.potions):
            return False
        potion = run_state.player.potions[slot_index]
        if potion is None:
            return False
        name = self.registry.potion(potion.potion_id).get("name", potion.potion_id)
        run_state.player.potions[slot_index] = None
        run_state.add_message(f"ポーション破棄: {name}")
        return True

    def can_use_in_combat(self, run_state: RunState, slot_index: int) -> tuple[bool, str]:
        if not 0 <= slot_index < len(run_state.player.potions):
            return False, "無効なスロットです"
        potion = run_state.player.potions[slot_index]
        if potion is None:
            return False, "空のスロットです"
        potion_def = self.registry.potion(potion.potion_id)
        usage = potion_def.get("usage", "combat")
        if usage not in {"combat", "any"}:
            return False, "戦闘中には使えません"
        return True, ""

    def use_in_combat(
        self,
        combat_system,
        slot_index: int,
        target: Optional[EnemyInstance] = None,
    ) -> bool:
        run_state = combat_system.run_state
        ok, reason = self.can_use_in_combat(run_state, slot_index)
        if not ok:
            combat_system.log(reason)
            return False
        potion = run_state.player.potions[slot_index]
        if potion is None:
            return False
        potion_def = self.registry.potion(potion.potion_id)
        if potion_def.get("target") == "enemy" and target is None:
            combat_system.log("対象を選んでください")
            return False

        name = potion_def.get("name", potion.potion_id)
        combat_system.log(f"{name} を使用")
        context = {
            "source": run_state.player,
            "target": target,
            "potion": potion,
            "potion_def": potion_def,
            "card_def": potion_def,
        }
        combat_system.executor.execute_many(potion_def.get("effects", []), context)
        run_state.player.potions[slot_index] = None
        combat_system._remove_dead_enemies()
        combat_system._check_victory_or_defeat()
        return True

    def use_out_of_combat(self, run_state: RunState, slot_index: int, executor) -> bool:
        if not 0 <= slot_index < len(run_state.player.potions):
            return False
        potion = run_state.player.potions[slot_index]
        if potion is None:
            return False
        potion_def = self.registry.potion(potion.potion_id)
        usage = potion_def.get("usage", "combat")
        if usage not in {"map", "any"}:
            run_state.add_message("今は使えません")
            return False
        executor.execute_many(run_state, potion_def.get("effects", []))
        name = potion_def.get("name", potion.potion_id)
        run_state.player.potions[slot_index] = None
        run_state.add_message(f"{name} を使用")
        return True

    def _weighted_choice(self, weighted: list[tuple[str, float]], rng: random.Random) -> str:
        total = sum(weight for _, weight in weighted)
        roll = rng.uniform(0, total)
        upto = 0.0
        for item_id, weight in weighted:
            upto += weight
            if roll <= upto:
                return item_id
        return weighted[-1][0]
