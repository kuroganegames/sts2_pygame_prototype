from __future__ import annotations

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


SUPPORTED_CONDITION_TYPES = {
    "runs_started_at_least",
    "runs_completed_at_least",
    "victories_at_least",
    "character_victories_at_least",
    "character_difficulty_victory_at_least",
    "character_difficulty_unlocked_at_least",
    "any_character_difficulty_unlocked_at_least",
    "enemy_seen",
    "enemy_defeated",
    "enemy_defeated_count_at_least",
    "card_seen",
    "card_acquired_count_at_least",
    "card_played_count_at_least",
    "relic_acquired",
    "potion_used",
    "potion_used_count_at_least",
    "modifier_applied",
    "modifier_applied_count_at_least",
    "ancient_choice",
    "timeline_unlocked",
    "achievement_unlocked",
    "unlocked_count_at_least",
    "timeline_count_at_least",
    "compendium_seen_count_at_least",
}


def condition_met(profile: ProfileState, condition: dict) -> bool:
    condition_type = condition.get("type")
    summary = profile.summary
    compendium = profile.compendium

    if condition_type == "runs_started_at_least":
        return int(summary.get("runs_started", 0)) >= int(condition.get("amount", 1))
    if condition_type == "runs_completed_at_least":
        return int(summary.get("runs_completed", 0)) >= int(condition.get("amount", 1))
    if condition_type == "victories_at_least":
        return int(summary.get("victories", 0)) >= int(condition.get("amount", 1))

    if condition_type == "character_victories_at_least":
        character_id = condition.get("character")
        stats = profile.characters.get(character_id, {})
        return int(stats.get("victories", 0)) >= int(condition.get("amount", 1))
    if condition_type == "character_difficulty_victory_at_least":
        character_id = condition.get("character")
        stats = profile.characters.get(character_id, {})
        return int(stats.get("highest_difficulty_victory", -1)) >= int(condition.get("level", 0))
    if condition_type == "character_difficulty_unlocked_at_least":
        character_id = condition.get("character")
        stats = profile.characters.get(character_id, {})
        return int(stats.get("highest_difficulty_unlocked", 0)) >= int(condition.get("level", 0))
    if condition_type == "any_character_difficulty_unlocked_at_least":
        level = int(condition.get("level", 0))
        return any(int(stats.get("highest_difficulty_unlocked", 0)) >= level for stats in profile.characters.values())

    if condition_type == "enemy_seen":
        enemy_id = condition.get("enemy")
        return bool(profile.bestiary.get(enemy_id, {}).get("seen", False))
    if condition_type == "enemy_defeated":
        enemy_id = condition.get("enemy")
        return int(profile.bestiary.get(enemy_id, {}).get("defeated", 0)) > 0
    if condition_type == "enemy_defeated_count_at_least":
        enemy_id = condition.get("enemy")
        return int(profile.bestiary.get(enemy_id, {}).get("defeated", 0)) >= int(condition.get("amount", 1))

    if condition_type == "card_seen":
        card_id = condition.get("card")
        return bool(compendium.get("cards", {}).get(card_id, {}).get("seen", False))
    if condition_type == "card_acquired_count_at_least":
        card_id = condition.get("card")
        return int(compendium.get("cards", {}).get(card_id, {}).get("acquired", 0)) >= int(condition.get("amount", 1))
    if condition_type == "card_played_count_at_least":
        card_id = condition.get("card")
        return int(compendium.get("cards", {}).get(card_id, {}).get("played", 0)) >= int(condition.get("amount", 1))

    if condition_type == "relic_acquired":
        relic_id = condition.get("relic")
        return int(compendium.get("relics", {}).get(relic_id, {}).get("acquired", 0)) > 0
    if condition_type == "potion_used":
        potion_id = condition.get("potion")
        return int(compendium.get("potions", {}).get(potion_id, {}).get("used", 0)) > 0
    if condition_type == "potion_used_count_at_least":
        potion_id = condition.get("potion")
        return int(compendium.get("potions", {}).get(potion_id, {}).get("used", 0)) >= int(condition.get("amount", 1))

    if condition_type == "modifier_applied":
        modifier_id = condition.get("modifier")
        return int(compendium.get("card_modifiers", {}).get(modifier_id, {}).get("applied", 0)) > 0
    if condition_type == "modifier_applied_count_at_least":
        modifier_id = condition.get("modifier")
        return int(compendium.get("card_modifiers", {}).get(modifier_id, {}).get("applied", 0)) >= int(condition.get("amount", 1))

    if condition_type == "ancient_choice":
        ancient_id = condition.get("ancient")
        choice_id = condition.get("choice")
        return int(compendium.get("ancients", {}).get(ancient_id, {}).get("choices", {}).get(choice_id, 0)) > 0

    if condition_type == "timeline_unlocked":
        fragment_id = condition.get("fragment")
        return fragment_id in set(profile.timeline.get("unlocked_fragments", []) or [])

    if condition_type == "achievement_unlocked":
        achievement_id = condition.get("achievement")
        return bool(profile.achievements.get(achievement_id, {}).get("unlocked"))

    if condition_type == "unlocked_count_at_least":
        target_type = condition.get("target_type")
        table_name = TARGET_TO_TABLE.get(str(target_type), f"{target_type}s")
        table = profile.unlocks.get(table_name, {}) or {}
        count = sum(1 for entry in table.values() if isinstance(entry, dict) and entry.get("unlocked"))
        return count >= int(condition.get("amount", 1))

    if condition_type == "timeline_count_at_least":
        return len(profile.timeline.get("unlocked_fragments", []) or []) >= int(condition.get("amount", 1))

    if condition_type == "compendium_seen_count_at_least":
        category = condition.get("category", "cards")
        amount = int(condition.get("amount", 1))
        entries = profile.compendium.get(category, {}) or {}
        return sum(1 for entry in entries.values() if isinstance(entry, dict) and entry.get("seen")) >= amount

    return False
