from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal
import uuid

CardZone = Literal[
    "master_deck",
    "hand",
    "draw_pile",
    "discard_pile",
    "exhaust_pile",
    "limbo",
]


def new_selection_id() -> str:
    return uuid.uuid4().hex


@dataclass
class CardSelectionRequest:
    title: str
    message: str
    source_zones: list[str]
    min_count: int = 1
    max_count: int = 1
    exact_count: int | None = None
    allow_skip: bool = False
    filter: dict[str, Any] = field(default_factory=dict)
    operation: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=new_selection_id)


@dataclass
class CardSelectionResult:
    request_id: str
    selected_instance_ids: list[str]
    skipped: bool = False


@dataclass
class CardSelectionCandidate:
    zone: str
    card: "CardInstance"
