from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SaveSlotSummary:
    slot_id: str
    slot_index: int
    path: Path
    exists: bool
    display_name: str = ""
    saved_at: str = ""
    current_scene: str = ""
    character_id: str = ""
    character_name: str = ""
    seed: int | None = None
    act: int = 0
    floor: int = 0
    hp: int = 0
    max_hp: int = 0
    gold: int = 0
    deck_size: int = 0
    relic_count: int = 0
    scene_label: str = ""
    is_corrupt: bool = False
    error: str = ""
