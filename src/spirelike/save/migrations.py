from __future__ import annotations

from spirelike.save.save_data import CURRENT_SAVE_SCHEMA_VERSION


class SaveMigrationError(ValueError):
    pass


def migrate_save(data: dict) -> dict:
    version = int(data.get("schema_version", 0))
    if version == CURRENT_SAVE_SCHEMA_VERSION:
        return data
    if version == 0:
        data = migrate_v0_to_v1(data)
        version = int(data.get("schema_version", 0))
    if version != CURRENT_SAVE_SCHEMA_VERSION:
        raise SaveMigrationError(f"Unsupported save schema: {version}")
    return data


def migrate_v0_to_v1(data: dict) -> dict:
    # 旧形式が存在しない段階なので、最低限の補完だけ行う。
    data.setdefault("schema_version", CURRENT_SAVE_SCHEMA_VERSION)
    data.setdefault("scene_payload", {})
    data.setdefault("rng_state", {})
    data.setdefault("content_snapshot", {})
    return data
