from __future__ import annotations

from spirelike.content.loader import ContentRegistry
from spirelike.profile.condition_progress import condition_progress
from spirelike.profile.profile_data import ProfileState


def format_condition(condition: dict, profile: ProfileState, registry: ContentRegistry) -> str:
    return condition_progress(condition, profile, registry).display()
