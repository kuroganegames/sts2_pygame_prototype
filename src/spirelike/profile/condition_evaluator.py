from __future__ import annotations

from spirelike.profile.profile_data import ProfileState


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

    return False
