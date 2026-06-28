from __future__ import annotations

from typing import Any

from spirelike.content.loader import ContentRegistry
from spirelike.profile.condition_evaluator import condition_met
from spirelike.profile.profile_data import ProfileState
from spirelike.profile.run_metrics import now_iso


class AchievementSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def achievements(self) -> list[dict[str, Any]]:
        return sorted(
            [item.data for item in self.registry.achievements.values()],
            key=lambda data: (str(data.get("category", "general")), str(data.get("id", ""))),
        )

    def is_unlocked(self, profile: ProfileState, achievement_id: str) -> bool:
        entry = profile.achievements.get(achievement_id)
        return bool(entry and entry.get("unlocked"))

    def unlock(self, profile: ProfileState, achievement: dict[str, Any]) -> bool:
        achievement_id = str(achievement.get("id"))
        if self.is_unlocked(profile, achievement_id):
            return False
        profile.achievements[achievement_id] = {
            "unlocked": True,
            "unlocked_at": now_iso(),
            "source": achievement_id,
        }
        return True

    def evaluate_achievements(
        self,
        profile: ProfileState,
        *,
        profile_eligible: bool = True,
    ) -> list[dict[str, Any]]:
        newly_unlocked: list[dict[str, Any]] = []
        for achievement in self.achievements():
            achievement_id = str(achievement.get("id"))
            if self.is_unlocked(profile, achievement_id):
                continue
            if achievement.get("profile_eligible_required", True) and not profile_eligible:
                continue
            conditions = achievement.get("conditions", []) or []
            if all(condition_met(profile, condition) for condition in conditions):
                if self.unlock(profile, achievement):
                    newly_unlocked.append(achievement)
        return newly_unlocked
