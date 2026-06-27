from __future__ import annotations

from typing import Any, Iterable

from spirelike.content.loader import ContentRegistry
from spirelike.profile.condition_evaluator import condition_met
from spirelike.profile.profile_data import ProfileState
from spirelike.profile.run_metrics import now_iso


TARGET_TO_TABLE = {
    "character": "characters",
    "card": "cards",
    "relic": "relics",
    "potion": "potions",
    "run_modifier": "run_modifiers",
    "ancient": "ancients",
    "card_modifier": "card_modifiers",
}


class UnlockSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry

    def rules(self) -> list[dict[str, Any]]:
        return [item.data for item in self.registry.unlock_rules.values()]

    def profile_table_name(self, target_type: str) -> str:
        return TARGET_TO_TABLE.get(target_type, f"{target_type}s")

    def rule_for(self, target_type: str, target_id: str) -> dict[str, Any] | None:
        for rule in self.rules():
            if rule.get("target_type") == target_type and rule.get("target_id") == target_id:
                return rule
        return None

    def is_unlocked(self, profile: ProfileState, target_type: str, target_id: str) -> bool:
        rule = self.rule_for(target_type, target_id)
        if rule is None:
            return True
        table_name = self.profile_table_name(target_type)
        entry = profile.unlocks.get(table_name, {}).get(target_id)
        return bool(entry and entry.get("unlocked"))

    def is_hidden_until_unlocked(self, target_type: str, target_id: str) -> bool:
        rule = self.rule_for(target_type, target_id)
        return bool(rule and rule.get("hidden_until_unlocked", False))

    def unlock(self, profile: ProfileState, rule: dict[str, Any], source: str | None = None) -> bool:
        target_type = str(rule.get("target_type"))
        target_id = str(rule.get("target_id"))
        table_name = self.profile_table_name(target_type)
        table = profile.unlocks.setdefault(table_name, {})
        entry = table.get(target_id)
        if entry and entry.get("unlocked"):
            return False
        table[target_id] = {
            "unlocked": True,
            "unlocked_at": now_iso(),
            "source": source or rule.get("id"),
        }
        return True

    def ensure_initial_unlocks(self, profile: ProfileState) -> list[dict[str, Any]]:
        newly_unlocked: list[dict[str, Any]] = []
        for rule in self.rules():
            if rule.get("initially_unlocked", False) and self.unlock(profile, rule, source=rule.get("id")):
                newly_unlocked.append(rule)
        return newly_unlocked

    def evaluate_unlocks(self, profile: ProfileState) -> list[dict[str, Any]]:
        newly_unlocked: list[dict[str, Any]] = []
        for rule in self.rules():
            target_type = str(rule.get("target_type"))
            target_id = str(rule.get("target_id"))
            if self.is_unlocked(profile, target_type, target_id):
                continue
            conditions = rule.get("conditions", []) or []
            if all(condition_met(profile, condition) for condition in conditions):
                if self.unlock(profile, rule, source=rule.get("id")):
                    newly_unlocked.append(rule)
        return newly_unlocked

    def unlocked_ids(self, profile: ProfileState, target_type: str, ids: Iterable[str]) -> list[str]:
        return [item_id for item_id in ids if self.is_unlocked(profile, target_type, item_id)]

    def build_unlocked_snapshot(self, profile: ProfileState) -> dict[str, list[str]]:
        return {
            "characters": self.unlocked_ids(profile, "character", self.registry.characters.keys()),
            "cards": self.unlocked_ids(profile, "card", self.registry.cards.keys()),
            "relics": self.unlocked_ids(profile, "relic", self.registry.relics.keys()),
            "potions": self.unlocked_ids(profile, "potion", self.registry.potions.keys()),
            "run_modifiers": self.unlocked_ids(profile, "run_modifier", self.registry.run_modifiers.keys()),
            "ancients": self.unlocked_ids(profile, "ancient", self.registry.ancients.keys()),
            "card_modifiers": self.unlocked_ids(profile, "card_modifier", self.registry.card_modifiers.keys()),
        }

    def run_has_unlocked(self, run_state, table_name: str, item_id: str) -> bool:
        snapshot = run_state.flags.get("unlocked_content")
        if not snapshot:
            return True
        return item_id in set(snapshot.get(table_name, []) or [])

    def filter_run_ids(self, run_state, table_name: str, ids: Iterable[str]) -> list[str]:
        return [item_id for item_id in ids if self.run_has_unlocked(run_state, table_name, item_id)]
