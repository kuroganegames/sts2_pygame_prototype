from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProgressionResult:
    new_timeline_fragments: list[dict[str, Any]] = field(default_factory=list)
    new_content_unlocks: list[dict[str, Any]] = field(default_factory=list)
    new_achievements: list[dict[str, Any]] = field(default_factory=list)
    new_difficulty_unlocks: list[dict[str, Any]] = field(default_factory=list)
    notifications: list[dict[str, Any]] = field(default_factory=list)

    def has_anything(self) -> bool:
        return bool(
            self.new_timeline_fragments
            or self.new_content_unlocks
            or self.new_achievements
            or self.new_difficulty_unlocks
        )
