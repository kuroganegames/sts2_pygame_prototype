from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

CURRENT_SAVE_SCHEMA_VERSION = 1


@dataclass
class SaveData:
    schema_version: int
    game_version: str
    saved_at: str
    current_scene: str
    scene_payload: dict[str, Any]
    run: dict[str, Any]
    rng_state: dict[str, Any] = field(default_factory=dict)
    content_snapshot: dict[str, Any] = field(default_factory=dict)
