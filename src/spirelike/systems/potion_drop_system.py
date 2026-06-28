from __future__ import annotations

from dataclasses import dataclass
import random

from spirelike.models.entities import RunState

POTION_DROP_CHANCE_FLAG = "potion_drop_chance"
INITIAL_POTION_DROP_CHANCE = 40.0
POTION_DROP_STEP = 10.0
ELITE_ROOM_BONUS = 12.5
MIN_POTION_DROP_CHANCE = 0.0
MAX_POTION_DROP_CHANCE = 100.0


@dataclass(frozen=True)
class PotionDropResult:
    dropped: bool
    roll: float
    base_chance_before: float
    room_bonus: float
    effective_chance: float
    base_chance_after: float
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "dropped": self.dropped,
            "roll": self.roll,
            "base_chance_before": self.base_chance_before,
            "room_bonus": self.room_bonus,
            "effective_chance": self.effective_chance,
            "base_chance_after": self.base_chance_after,
            "reason": self.reason,
        }


class PotionDropSystem:
    def current_chance(self, run_state: RunState) -> float:
        return float(run_state.flags.get(POTION_DROP_CHANCE_FLAG, INITIAL_POTION_DROP_CHANCE))

    def set_chance(self, run_state: RunState, value: float) -> None:
        run_state.flags[POTION_DROP_CHANCE_FLAG] = max(
            MIN_POTION_DROP_CHANCE,
            min(MAX_POTION_DROP_CHANCE, float(value)),
        )

    def room_bonus(self, node_type: str) -> float:
        return ELITE_ROOM_BONUS if node_type == "elite" else 0.0

    def roll_drop(
        self,
        run_state: RunState,
        rng: random.Random,
        *,
        node_type: str,
        can_receive_potion: bool,
    ) -> PotionDropResult:
        before = self.current_chance(run_state)
        bonus = self.room_bonus(node_type)
        if not can_receive_potion:
            return PotionDropResult(
                dropped=False,
                roll=0.0,
                base_chance_before=before,
                room_bonus=bonus,
                effective_chance=0.0,
                base_chance_after=before,
                reason="no_empty_slot",
            )

        effective = max(MIN_POTION_DROP_CHANCE, min(MAX_POTION_DROP_CHANCE, before + bonus))
        roll = rng.uniform(0, 100)
        dropped = roll < effective
        after = before - POTION_DROP_STEP if dropped else before + POTION_DROP_STEP
        self.set_chance(run_state, after)
        return PotionDropResult(
            dropped=dropped,
            roll=roll,
            base_chance_before=before,
            room_bonus=bonus,
            effective_chance=effective,
            base_chance_after=self.current_chance(run_state),
        )
