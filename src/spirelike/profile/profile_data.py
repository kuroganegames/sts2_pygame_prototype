from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

CURRENT_PROFILE_SCHEMA_VERSION = 1


def default_summary() -> dict[str, Any]:
    return {
        "runs_started": 0,
        "runs_completed": 0,
        "victories": 0,
        "defeats": 0,
        "highest_floor": 0,
        "highest_act": 0,
        "total_enemies_defeated": 0,
        "total_gold_gained": 0,
        "total_cards_added": 0,
    }


def default_compendium() -> dict[str, dict[str, Any]]:
    return {
        "cards": {},
        "relics": {},
        "potions": {},
        "card_modifiers": {},
        "ancients": {},
    }


def default_unlocks() -> dict[str, dict[str, Any]]:
    return {
        "characters": {},
        "cards": {},
        "relics": {},
        "potions": {},
        "run_modifiers": {},
        "ancients": {},
        "card_modifiers": {},
    }


def default_achievements() -> dict[str, dict[str, Any]]:
    return {}


@dataclass
class ProfileState:
    schema_version: int = CURRENT_PROFILE_SCHEMA_VERSION
    game_version: str = "0.1.0"
    created_at: str = ""
    updated_at: str = ""
    summary: dict[str, Any] = field(default_factory=default_summary)
    characters: dict[str, dict[str, Any]] = field(default_factory=dict)
    run_history: list[dict[str, Any]] = field(default_factory=list)
    bestiary: dict[str, dict[str, Any]] = field(default_factory=dict)
    compendium: dict[str, dict[str, Any]] = field(default_factory=default_compendium)
    timeline: dict[str, Any] = field(default_factory=lambda: {"unlocked_fragments": []})
    unlocks: dict[str, dict[str, Any]] = field(default_factory=default_unlocks)
    achievements: dict[str, dict[str, Any]] = field(default_factory=default_achievements)
    notifications: list[dict[str, Any]] = field(default_factory=list)

    def ensure_defaults(self) -> None:
        base_summary = default_summary()
        for key, value in base_summary.items():
            self.summary.setdefault(key, value)
        base_compendium = default_compendium()
        for key, value in base_compendium.items():
            self.compendium.setdefault(key, value)
        base_unlocks = default_unlocks()
        for key, value in base_unlocks.items():
            self.unlocks.setdefault(key, value)
        if not isinstance(self.achievements, dict):
            self.achievements = {}
        if not isinstance(self.notifications, list):
            self.notifications = []
        self.timeline.setdefault("unlocked_fragments", [])
