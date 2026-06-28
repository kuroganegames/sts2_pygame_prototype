from __future__ import annotations

from dataclasses import dataclass

from spirelike.content.loader import ContentRegistry
from spirelike.profile.profile_data import ProfileState


TARGET_TO_TABLE = {
    "character": "characters",
    "card": "cards",
    "relic": "relics",
    "potion": "potions",
    "run_modifier": "run_modifiers",
    "ancient": "ancients",
    "card_modifier": "card_modifiers",
}


@dataclass
class ConditionProgress:
    label: str
    current: int
    required: int
    complete: bool

    @property
    def ratio(self) -> float:
        if self.required <= 0:
            return 1.0 if self.complete else 0.0
        return min(1.0, max(0.0, self.current / self.required))

    def display(self) -> str:
        if self.required == 1 and self.current in {0, 1}:
            return f"{self.label}: {'達成' if self.complete else '未達成'}"
        return f"{self.label}: {self.current}/{self.required}"


def condition_progress(condition: dict, profile: ProfileState, registry: ContentRegistry) -> ConditionProgress:
    condition_type = condition.get("type")

    if condition_type == "victories_at_least":
        required = int(condition.get("amount", 1))
        current = int(profile.summary.get("victories", 0))
        return ConditionProgress("勝利数", min(current, required), required, current >= required)

    if condition_type == "runs_completed_at_least":
        required = int(condition.get("amount", 1))
        current = int(profile.summary.get("runs_completed", 0))
        return ConditionProgress("完了ラン", min(current, required), required, current >= required)

    if condition_type == "enemy_defeated_count_at_least":
        enemy_id = condition.get("enemy")
        required = int(condition.get("amount", 1))
        current = int(profile.bestiary.get(enemy_id, {}).get("defeated", 0))
        name = registry.enemy(enemy_id).get("name", enemy_id) if enemy_id in registry.enemies else str(enemy_id)
        return ConditionProgress(f"{name}撃破", min(current, required), required, current >= required)

    if condition_type == "achievement_unlocked":
        achievement_id = condition.get("achievement")
        current = 1 if profile.achievements.get(achievement_id, {}).get("unlocked") else 0
        name = registry.achievement(achievement_id).get("name", achievement_id) if achievement_id in registry.achievements else str(achievement_id)
        return ConditionProgress(f"実績「{name}」", current, 1, current >= 1)

    if condition_type == "character_difficulty_unlocked_at_least":
        character_id = condition.get("character")
        required = int(condition.get("level", 0))
        stats = profile.characters.get(character_id, {})
        current = int(stats.get("highest_difficulty_unlocked", 0))
        name = registry.character(character_id).get("name", character_id) if character_id in registry.characters else str(character_id)
        return ConditionProgress(f"{name} Difficulty解放", min(current, required), required, current >= required)

    if condition_type == "character_difficulty_victory_at_least":
        character_id = condition.get("character")
        required = int(condition.get("level", 0))
        stats = profile.characters.get(character_id, {})
        current = int(stats.get("highest_difficulty_victory", -1))
        current_display = max(0, current)
        name = registry.character(character_id).get("name", character_id) if character_id in registry.characters else str(character_id)
        return ConditionProgress(f"{name} Difficulty勝利", min(current_display, required), required, current >= required)

    if condition_type == "timeline_unlocked":
        fragment_id = condition.get("fragment")
        current = 1 if fragment_id in set(profile.timeline.get("unlocked_fragments", []) or []) else 0
        title = registry.timeline_fragment(fragment_id).get("title", fragment_id) if fragment_id in registry.timeline_fragments else str(fragment_id)
        return ConditionProgress(f"Timeline「{title}」", current, 1, current >= 1)

    if condition_type == "potion_used":
        potion_id = condition.get("potion")
        current = 1 if int(profile.compendium.get("potions", {}).get(potion_id, {}).get("used", 0)) > 0 else 0
        name = registry.potion(potion_id).get("name", potion_id) if potion_id in registry.potions else str(potion_id)
        return ConditionProgress(f"{name}使用", current, 1, current >= 1)

    if condition_type == "unlocked_count_at_least":
        target_type = condition.get("target_type")
        table_name = TARGET_TO_TABLE.get(str(target_type), f"{target_type}s")
        table = profile.unlocks.get(table_name, {}) or {}
        current = sum(1 for entry in table.values() if isinstance(entry, dict) and entry.get("unlocked"))
        required = int(condition.get("amount", 1))
        return ConditionProgress(f"{target_type}解放数", min(current, required), required, current >= required)

    return ConditionProgress(str(condition_type or "条件"), 0, 1, False)
