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
from spirelike.save.save_slot import SaveSlotSummary
from spirelike.save.serializer import (
    reward_bundle_from_dict,
    reward_bundle_to_dict,
    run_state_from_dict,
    run_state_to_dict,
)
from spirelike.save.validation import validate_combat_snapshot, validate_loaded_run


class SaveSystemError(RuntimeError):
    pass


class SaveSystem:
    DEFAULT_SLOT_COUNT = 3

    def __init__(self, project_root: Path, registry: ContentRegistry) -> None:
        self.project_root = project_root
        self.registry = registry
        self.save_dir = project_root / "saves"
        self.slots_dir = self.save_dir / "slots"
        self.legacy_path = self.save_dir / "save_001.json"
        self.default_path = self.legacy_path

    def slot_id_for_index(self, index: int) -> str:
        return f"slot_{index:03d}"

    def slot_index(self, slot_id: str) -> int:
        try:
            return int(str(slot_id).split("_")[-1])
        except (TypeError, ValueError):
            return 1

    def slot_path(self, slot_id: str) -> Path:
        return self.slots_dir / f"{slot_id}.json"

    def save_exists(self) -> bool:
        return self.any_save_exists()

    def any_save_exists(self) -> bool:
        return any(slot.exists and not slot.is_corrupt for slot in self.list_slots())

    def list_slots(self) -> list[SaveSlotSummary]:
        self.migrate_legacy_save_if_needed()
        return [
            self.read_slot_summary(self.slot_id_for_index(index), index, self.slot_path(self.slot_id_for_index(index)))
            for index in range(1, self.DEFAULT_SLOT_COUNT + 1)
        ]

    def latest_slot(self) -> SaveSlotSummary | None:
        slots = [slot for slot in self.list_slots() if slot.exists and not slot.is_corrupt]
        if not slots:
            return None
        return max(slots, key=lambda slot: slot.saved_at or "")

    def read_slot_summary(self, slot_id: str, index: int, path: Path) -> SaveSlotSummary:
        display_name = f"Slot {index}"
        if not path.exists():
            return SaveSlotSummary(
                slot_id=slot_id,
                slot_index=index,
                path=path,
                exists=False,
                display_name=display_name,
                scene_label="空き",
            )
        try:
            data = migrate_save(json.loads(path.read_text(encoding="utf-8")))
            run = data["run"]
            flags = run.get("flags", {}) or {}
            config = flags.get("run_config", {}) or {}
            player = run["player"]
            character_id = str(run.get("character_id", player.get("character_id", "")))
            if character_id in self.registry.characters:
                character_name = self.registry.character(character_id).get("name", character_id)
            else:
                character_name = character_id or "?"
            current_scene = str(data.get("current_scene", "map"))
            return SaveSlotSummary(
                slot_id=slot_id,
                slot_index=index,
                path=path,
                exists=True,
                display_name=str(data.get("display_name", display_name)),
                saved_at=str(data.get("saved_at", "")),
                current_scene=current_scene,
                scene_label=self.scene_label(current_scene),
                character_id=character_id,
                character_name=character_name,
                seed=int(run.get("seed", 0)),
                act=int(run.get("act", 0)),
                floor=int(run.get("floor", 0)),
                hp=int(player.get("hp", 0)),
                max_hp=int(player.get("max_hp", 0)),
                gold=int(player.get("gold", 0)),
                deck_size=len(player.get("deck", []) or []),
                relic_count=len(player.get("relics", []) or []),
                mode=str(config.get("mode", "standard")),
                custom=bool(config.get("custom", False)),
                modifiers=list(config.get("selected_modifiers", []) or []),
                difficulty_level=int(config.get("difficulty_level", 0)),
            )
        except Exception as exc:
            return SaveSlotSummary(
                slot_id=slot_id,
                slot_index=index,
                path=path,
                exists=True,
                display_name=display_name,
                scene_label="破損",
                is_corrupt=True,
                error=str(exc),
            )

    def save_run(
        self,
        run_state: RunState,
        *,
        current_scene: str,
        scene_payload: dict[str, Any] | None = None,
        slot_id: str | None = None,
    ) -> None:
        self.slots_dir.mkdir(parents=True, exist_ok=True)
        slot_id = slot_id or run_state.flags.get("save_slot_id") or "slot_001"
        run_state.flags["save_slot_id"] = slot_id
        slot_index = self.slot_index(slot_id)
        data = {
            "schema_version": CURRENT_SAVE_SCHEMA_VERSION,
            "save_slot_id": slot_id,
            "display_name": f"Slot {slot_index}",
            "game_version": __version__,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "current_scene": current_scene,
            "scene_payload": scene_payload or {},
            "run": run_state_to_dict(run_state),
            "rng_state": {},
            "content_snapshot": self.build_content_snapshot(),
        }
        self._atomic_write(self.slot_path(slot_id), data)

    def load_run(self, slot_id: str | None = None) -> tuple[RunState, str, dict[str, Any]]:
        self.migrate_legacy_save_if_needed()
        if slot_id is None:
            latest = self.latest_slot()
            if latest is None:
                raise SaveSystemError("セーブデータがありません")
            slot_id = latest.slot_id
        path = self.slot_path(slot_id)
        if not path.exists():
            raise SaveSystemError(f"スロットが空です: {slot_id}")
        return self._load_from_path(path, slot_id)

    def load_latest_run(self) -> tuple[RunState, str, dict[str, Any]]:
        return self.load_run(None)

    def _load_from_path(self, path: Path, slot_id: str) -> tuple[RunState, str, dict[str, Any]]:
        raw = json.loads(path.read_text(encoding="utf-8"))
        data = migrate_save(raw)
        data["save_slot_id"] = slot_id
        scene_name = str(data.get("current_scene", "map"))
        scene_payload = dict(data.get("scene_payload", {}) or {})
        run_state = run_state_from_dict(data["run"])
        run_state.flags["save_slot_id"] = slot_id
        warnings = validate_loaded_run(run_state, self.registry)

        if scene_name == "combat" and scene_payload.get("combat_snapshot"):
            warnings.extend(validate_combat_snapshot(scene_payload["combat_snapshot"], self.registry))

        for warning in warnings[-5:]:
            run_state.add_message(warning)

        payload = self._restore_scene_payload(scene_name, scene_payload)
        payload["run_state"] = run_state
        return run_state, scene_name, payload

    def delete_slot(self, slot_id: str | None) -> None:
        if not slot_id:
            return
        path = self.slot_path(slot_id)
        if path.exists():
            path.unlink()

    def delete_save(self, slot_id: str | None = None) -> None:
        if slot_id:
            self.delete_slot(slot_id)
            return
        latest = self.latest_slot()
        if latest:
            self.delete_slot(latest.slot_id)
        elif self.legacy_path.exists():
            self.legacy_path.unlink()

    def migrate_legacy_save_if_needed(self) -> None:
        if not self.legacy_path.exists():
            return
        self.slots_dir.mkdir(parents=True, exist_ok=True)
        target = self.slot_path("slot_001")
        backup = self.save_dir / "save_001.migrated.bak"
        if target.exists():
            if backup.exists():
                backup.unlink()
            self.legacy_path.replace(backup)
            return
        data = migrate_save(json.loads(self.legacy_path.read_text(encoding="utf-8")))
        data["save_slot_id"] = "slot_001"
        data["display_name"] = "Slot 1"
        run = data.get("run", {}) or {}
        flags = run.setdefault("flags", {})
        flags["save_slot_id"] = "slot_001"
        self._atomic_write(target, data)
        if backup.exists():
            backup.unlink()
        self.legacy_path.replace(backup)

    def build_content_snapshot(self) -> dict[str, int]:
        return {
            "cards": len(self.registry.cards),
            "relics": len(self.registry.relics),
            "potions": len(self.registry.potions),
            "ancients": len(self.registry.ancients),
            "card_modifiers": len(self.registry.card_modifiers),
            "run_modifiers": len(self.registry.run_modifiers),
            "difficulty_levels": len(self.registry.difficulty_levels),
            "maps": len(self.registry.maps),
            "events": len(self.registry.events),
        }

    def scene_label(self, scene_name: str) -> str:
        return {
            "map": "マップ",
            "combat": "戦闘中",
            "reward": "報酬",
            "rest": "休憩所",
            "shop": "ショップ",
            "event": "イベント",
            "ancient": "エンシェント",
        }.get(scene_name, scene_name)

    def _restore_scene_payload(self, scene_name: str, scene_payload: dict[str, Any]) -> dict[str, Any]:
        payload = dict(scene_payload)
        if scene_name == "reward" and isinstance(payload.get("reward"), dict):
            payload["reward"] = reward_bundle_from_dict(payload["reward"])
        return payload

    def _atomic_write(self, path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        json_text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
        tmp_path = path.with_suffix(".tmp")
        tmp_path.write_text(json_text, encoding="utf-8")
        tmp_path.replace(path)

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
        if scene_name == "combat":
            return {
                "node_id": payload.get("node_id"),
                "node_type": payload.get("node_type", "monster"),
                "enemy_ids": list(payload.get("enemy_ids", []) or []),
                "combat_snapshot": payload.get("combat_snapshot"),
            }
        return {}
