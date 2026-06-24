from __future__ import annotations

import random
from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import AncientBlessingInstance, RunState


class AncientSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def candidates_for_act(self, act: int) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        for item in self.registry.ancients.values():
            data = item.data
            act_pool = data.get("act_pool", []) or []
            if not act_pool or act in act_pool:
                candidates.append(data)
        return candidates

    def choose_ancient(self, run_state: RunState, rng: random.Random) -> dict[str, Any] | None:
        already_seen = set(run_state.flags.get("seen_ancients", []))
        candidates = [
            ancient
            for ancient in self.candidates_for_act(run_state.act)
            if ancient.get("id") not in already_seen
        ]
        if not candidates:
            candidates = self.candidates_for_act(run_state.act)
        if not candidates:
            return None
        weighted = [(ancient, float(ancient.get("weight", 100))) for ancient in candidates]
        total = sum(max(0.0, weight) for _, weight in weighted)
        if total <= 0:
            return candidates[0]
        roll = rng.uniform(0, total)
        upto = 0.0
        for ancient, weight in weighted:
            upto += max(0.0, weight)
            if roll <= upto:
                return ancient
        return candidates[-1]

    def apply_choice(self, run_state: RunState, ancient_def: dict[str, Any], choice: dict[str, Any], executor) -> None:
        ancient_id = str(ancient_def["id"])
        choice_id = str(choice["id"])
        executor.execute_many(run_state, choice.get("effects", []))
        if choice.get("triggers"):
            run_state.ancient_blessings.append(
                AncientBlessingInstance(ancient_id=ancient_id, choice_id=choice_id)
            )
        seen = set(run_state.flags.get("seen_ancients", []))
        seen.add(ancient_id)
        run_state.flags["seen_ancients"] = sorted(seen)
        run_state.add_message(
            f"エンシェント: {ancient_def.get('name', ancient_id)} / {choice.get('name', choice_id)}"
        )

    def find_choice(self, ancient_def: dict[str, Any], choice_id: str) -> dict[str, Any] | None:
        for choice in ancient_def.get("choices", []) or []:
            if choice.get("id") == choice_id:
                return choice
        return None
