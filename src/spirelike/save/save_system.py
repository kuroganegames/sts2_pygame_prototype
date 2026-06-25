from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from spirelike import __version__
from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import RunState
from spirelike.save.migrations import migrate_save
from spirelike.save.save_data import CURRENT_SAVE_SCHEMA_VERSION
from spirelike.save.serializer import (
    reward_bundle_from_dict,
    reward_bundle_to_dict,
    run_state_from_dict,
    run_state_to_dict,
)
from spirelike.save.validation import validate_loaded_run


class SaveSystemError(RuntimeError):
    pass


class SaveSystem:
    def __init__(self, project_root: Path, registry: ContentRegistry) -> None:
        self.project_root = project_root
        self.registry = registry
        self.save_dir = project_root / "saves"
        self.default_path = self.save_dir / "save_001.json"

    def save_exists(self) -> bool:
        return self.default_path.exists()

    def save_run(
        self,
        run_state: RunState,
        *,
        current_scene: str,
        scene_payload: dict[str, Any] | None = None,
    ) -> None:
        self.save_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": CURRENT_SAVE_SCHEMA_VERSION,
            "game_version": __version__,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "current_scene": current_scene,
            "scene_payload": scene_payload or {},
            "run": run_state_to_dict(run_state),
            "rng_state": {},
            "content_snapshot": self.build_content_snapshot(),
        }
        json_text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        tmp_path = self.default_path.with_suffix(".tmp")
        tmp_path.write_text(json_text, encoding="utf-8")
        tmp_path.replace(self.default_path)

    def load_run(self) -> tuple[RunState, str, dict[str, Any]]:
        if not self.default_path.exists():
            raise SaveSystemError("セーブデータがありません")
        raw = json.loads(self.default_path.read_text(encoding="utf-8"))
        data = migrate_save(raw)
        scene_name = str(data.get("current_scene", "map"))
        scene_payload = dict(data.get("scene_payload", {}) or {})
        run_state = run_state_from_dict(data["run"])
        warnings = validate_loaded_run(run_state, self.registry)
        for warning in warnings[-5:]:
            run_state.add_message(warning)

        payload = self._restore_scene_payload(scene_name, scene_payload)
        payload["run_state"] = run_state
        return run_state, scene_name, payload

    def delete_save(self) -> None:
        if self.default_path.exists():
            self.default_path.unlink()

    def build_content_snapshot(self) -> dict[str, int]:
        return {
            "cards": len(self.registry.cards),
            "relics": len(self.registry.relics),
            "potions": len(self.registry.potions),
            "ancients": len(self.registry.ancients),
            "card_modifiers": len(self.registry.card_modifiers),
            "maps": len(self.registry.maps),
            "events": len(self.registry.events),
        }

    def _restore_scene_payload(self, scene_name: str, scene_payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(scene_payload)
        if scene_name == "reward" and isinstance(payload.get("reward"), dict):
            payload["reward"] = reward_bundle_from_dict(payload["reward"])
        return payload

    @staticmethod
    def safe_scene_payload(scene_name: str, payload: dict[str, Any] | None) -> dict[str, Any]:
        payload = payload or {}
        if scene_name == "map":
            return {}
        if scene_name in {"rest", "shop", "event", "ancient"}:
            result: dict[str, Any] = {}
            for key in ("node_id", "after", "phase"):
                if key in payload and payload.get(key) is not None:
                    result[key] = payload.get(key)
            return result
        if scene_name == "reward":
            return {
                "node_id": payload.get("node_id"),
                "reward": reward_bundle_to_dict(payload.get("reward")),
                "after_boss": bool(payload.get("after_boss", False)),
            }
        return {}
