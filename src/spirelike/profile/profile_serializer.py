from __future__ import annotations

from spirelike.profile.profile_data import ProfileState, CURRENT_PROFILE_SCHEMA_VERSION, default_compendium, default_summary


def profile_to_dict(profile: ProfileState) -> dict:
    profile.ensure_defaults()
    return {
        "schema_version": profile.schema_version,
        "game_version": profile.game_version,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
        "summary": dict(profile.summary),
        "characters": dict(profile.characters),
        "run_history": list(profile.run_history),
        "bestiary": dict(profile.bestiary),
        "compendium": dict(profile.compendium),
        "timeline": dict(profile.timeline),
    }


def profile_from_dict(data: dict) -> ProfileState:
    profile = ProfileState(
        schema_version=int(data.get("schema_version", CURRENT_PROFILE_SCHEMA_VERSION)),
        game_version=str(data.get("game_version", "0.1.0")),
        created_at=str(data.get("created_at", "")),
        updated_at=str(data.get("updated_at", "")),
        summary=dict(data.get("summary", {}) or default_summary()),
        characters=dict(data.get("characters", {}) or {}),
        run_history=list(data.get("run_history", []) or []),
        bestiary=dict(data.get("bestiary", {}) or {}),
        compendium=dict(data.get("compendium", {}) or default_compendium()),
        timeline=dict(data.get("timeline", {}) or {"unlocked_fragments": []}),
    )
    profile.ensure_defaults()
    return profile
