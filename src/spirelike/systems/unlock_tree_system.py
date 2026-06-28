from __future__ import annotations

from dataclasses import dataclass

from spirelike.content.loader import ContentRegistry
from spirelike.profile.condition_formatter import format_condition
from spirelike.profile.profile_data import ProfileState
from spirelike.systems.unlock_system import UnlockSystem


@dataclass
class UnlockNode:
    unlock_id: str
    target_type: str
    target_id: str
    name: str
    description: str
    category: str
    tier: int
    order: int
    unlocked: bool
    hidden: bool
    condition_lines: list[str]


class UnlockTreeSystem:
    def __init__(self, registry: ContentRegistry) -> None:
        self.registry = registry
        self.unlocks = UnlockSystem(registry)

    def nodes(self, profile: ProfileState, category: str = "all") -> list[UnlockNode]:
        result: list[UnlockNode] = []
        for unlock_id, item in self.registry.unlock_rules.items():
            rule = item.data
            rule_category = str(rule.get("category", rule.get("target_type", "other")))
            if category != "all" and rule_category != category:
                continue
            target_type = str(rule.get("target_type"))
            target_id = str(rule.get("target_id"))
            unlocked = self.unlocks.is_unlocked(profile, target_type, target_id)
            hidden = bool(rule.get("hidden_until_unlocked", False)) and not unlocked
            conditions = rule.get("conditions", []) or []
            condition_lines = [format_condition(condition, profile, self.registry) for condition in conditions]
            if not condition_lines and rule.get("initially_unlocked", False):
                condition_lines = ["初期解放"]
            name = "???" if hidden else str(rule.get("name", target_id))
            description = "隠された条件" if hidden else str(rule.get("description", ""))
            result.append(
                UnlockNode(
                    unlock_id=unlock_id,
                    target_type=target_type,
                    target_id=target_id,
                    name=name,
                    description=description,
                    category=rule_category,
                    tier=int(rule.get("tier", 99)),
                    order=int(rule.get("order", 999)),
                    unlocked=unlocked,
                    hidden=hidden,
                    condition_lines=condition_lines,
                )
            )
        return sorted(result, key=lambda node: (node.tier, node.order, node.unlock_id))
