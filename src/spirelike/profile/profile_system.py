from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from spirelike import __version__
from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import RunState
from spirelike.profile.profile_data import ProfileState, CURRENT_PROFILE_SCHEMA_VERSION
from spirelike.profile.profile_serializer import profile_from_dict, profile_to_dict
from spirelike.profile.run_metrics import RunMetricsSystem, now_iso
from spirelike.profile.timeline_conditions import condition_met


class ProfileSystem:
    def __init__(self, project_root: Path, registry: ContentRegistry) -> None:
        self.project_root = project_root
        self.registry = registry
        self.profile_path = project_root / "saves" / "profile.json"
        self.profile = self.load_or_create()

    def load_or_create(self) -> ProfileState:
        if self.profile_path.exists():
            data = json.loads(self.profile_path.read_text(encoding="utf-8"))
            profile = profile_from_dict(data)
            profile.ensure_defaults()
            return profile
        now = now_iso()
        profile = ProfileState(
            schema_version=CURRENT_PROFILE_SCHEMA_VERSION,
            game_version=__version__,
            created_at=now,
            updated_at=now,
        )
        profile.ensure_defaults()
        return profile

    def save(self) -> None:
        self.profile.ensure_defaults()
        self.profile.updated_at = now_iso()
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(profile_to_dict(self.profile), ensure_ascii=False, indent=2, sort_keys=True)
        tmp_path = self.profile_path.with_suffix(".tmp")
        tmp_path.write_text(text, encoding="utf-8")
        tmp_path.replace(self.profile_path)

    def record_run_started(self, run_state: RunState) -> None:
        if run_state.flags.get("profile_run_started_recorded"):
            return
        RunMetricsSystem.ensure(run_state)
        self.profile.summary["runs_started"] = int(self.profile.summary.get("runs_started", 0)) + 1
        char_stats = self._character_stats(run_state.character_id)
        char_stats["runs_started"] = int(char_stats.get("runs_started", 0)) + 1
        for card in run_state.player.deck:
            RunMetricsSystem.record_card_acquired(run_state, card.card_id)
        for relic in run_state.player.relics:
            RunMetricsSystem.record_relic_acquired(run_state, relic.relic_id)
        run_state.flags["profile_run_started_recorded"] = True
        self.save()

    def finalize_run(self, run_state: RunState, result: str) -> None:
        metrics = RunMetricsSystem.ensure(run_state)
        run_id = metrics.get("run_id")
        if any(record.get("run_id") == run_id for record in self.profile.run_history):
            return
        record = self.build_run_record(run_state, result, metrics)
        self.profile.run_history.insert(0, record)
        self.profile.run_history = self.profile.run_history[:100]
        self.apply_metrics_to_profile(run_state, result, metrics)
        new_fragments = self.update_timeline_unlocks()
        for fragment_id in new_fragments:
            title = self.registry.timeline_fragment(fragment_id).get("title", fragment_id)
            run_state.add_message(f"Timeline解放: {title}")
        self.save()

    def build_run_record(self, run_state: RunState, result: str, metrics: dict[str, Any]) -> dict[str, Any]:
        player = run_state.player
        return {
            "run_id": metrics.get("run_id"),
            "seed": run_state.seed,
            "character_id": run_state.character_id,
            "result": result,
            "started_at": metrics.get("started_at"),
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "act": run_state.act,
            "floor": run_state.floor,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "gold": player.gold,
            "deck_size": len(player.deck),
            "deck": [
                {
                    "card_id": card.card_id,
                    "upgraded": card.upgraded,
                    "modifiers": [modifier.modifier_id for modifier in card.modifiers],
                }
                for card in player.deck
            ],
            "relics": [relic.relic_id for relic in player.relics],
            "potions": [potion.potion_id if potion else None for potion in player.potions],
            "ancient_blessings": [
                {"ancient_id": blessing.ancient_id, "choice_id": blessing.choice_id}
                for blessing in run_state.ancient_blessings
            ],
            "enemies_defeated": dict(metrics.get("enemies_defeated", {})),
            "cards_played": dict(metrics.get("cards_played", {})),
            "modifiers_applied": dict(metrics.get("modifiers_applied", {})),
        }

    def apply_metrics_to_profile(self, run_state: RunState, result: str, metrics: dict[str, Any]) -> None:
        summary = self.profile.summary
        summary["runs_completed"] = int(summary.get("runs_completed", 0)) + 1
        if result == "victory":
            summary["victories"] = int(summary.get("victories", 0)) + 1
        else:
            summary["defeats"] = int(summary.get("defeats", 0)) + 1
        summary["highest_floor"] = max(int(summary.get("highest_floor", 0)), run_state.floor)
        summary["highest_act"] = max(int(summary.get("highest_act", 0)), run_state.act)
        summary["total_gold_gained"] = int(summary.get("total_gold_gained", 0)) + int(metrics.get("gold_gained", 0))
        summary["total_cards_added"] = int(summary.get("total_cards_added", 0)) + sum(metrics.get("cards_acquired", {}).values())
        enemies_defeated_total = sum(metrics.get("enemies_defeated", {}).values())
        summary["total_enemies_defeated"] = int(summary.get("total_enemies_defeated", 0)) + enemies_defeated_total

        char_stats = self._character_stats(run_state.character_id)
        char_stats["runs_completed"] = int(char_stats.get("runs_completed", 0)) + 1
        char_stats["highest_floor"] = max(int(char_stats.get("highest_floor", 0)), run_state.floor)
        char_stats["highest_act"] = max(int(char_stats.get("highest_act", 0)), run_state.act)
        if result == "victory":
            char_stats["victories"] = int(char_stats.get("victories", 0)) + 1

        self._apply_bestiary(metrics)
        self._apply_compendium(metrics)

    def _character_stats(self, character_id: str) -> dict[str, Any]:
        return self.profile.characters.setdefault(
            character_id,
            {"runs_started": 0, "runs_completed": 0, "victories": 0, "highest_floor": 0, "highest_act": 0},
        )

    def _entry(self, table: dict[str, dict[str, Any]], item_id: str) -> dict[str, Any]:
        entry = table.setdefault(item_id, {})
        if not entry.get("seen"):
            entry["seen"] = True
            entry["first_seen_at"] = now_iso()
        entry["last_seen_at"] = now_iso()
        return entry

    def _apply_bestiary(self, metrics: dict[str, Any]) -> None:
        for enemy_id, count in metrics.get("enemies_seen", {}).items():
            entry = self._entry(self.profile.bestiary, enemy_id)
            entry["encountered"] = int(entry.get("encountered", 0)) + int(count)
        for enemy_id, count in metrics.get("enemies_defeated", {}).items():
            entry = self._entry(self.profile.bestiary, enemy_id)
            entry["defeated"] = int(entry.get("defeated", 0)) + int(count)

    def _apply_compendium(self, metrics: dict[str, Any]) -> None:
        comp = self.profile.compendium
        for card_id, count in metrics.get("cards_seen", {}).items():
            self._entry(comp["cards"], card_id)
        for card_id, count in metrics.get("cards_acquired", {}).items():
            entry = self._entry(comp["cards"], card_id)
            entry["acquired"] = int(entry.get("acquired", 0)) + int(count)
        for card_id, count in metrics.get("cards_played", {}).items():
            entry = self._entry(comp["cards"], card_id)
            entry["played"] = int(entry.get("played", 0)) + int(count)
        for card_id, count in metrics.get("cards_upgraded", {}).items():
            entry = self._entry(comp["cards"], card_id)
            entry["upgraded"] = int(entry.get("upgraded", 0)) + int(count)
        for card_id, count in metrics.get("cards_removed", {}).items():
            entry = self._entry(comp["cards"], card_id)
            entry["removed"] = int(entry.get("removed", 0)) + int(count)
        for card_id, count in metrics.get("cards_transformed", {}).items():
            entry = self._entry(comp["cards"], card_id)
            entry["transformed"] = int(entry.get("transformed", 0)) + int(count)

        for relic_id, count in metrics.get("relics_acquired", {}).items():
            entry = self._entry(comp["relics"], relic_id)
            entry["acquired"] = int(entry.get("acquired", 0)) + int(count)
        for potion_id, count in metrics.get("potions_acquired", {}).items():
            entry = self._entry(comp["potions"], potion_id)
            entry["acquired"] = int(entry.get("acquired", 0)) + int(count)
        for potion_id, count in metrics.get("potions_used", {}).items():
            entry = self._entry(comp["potions"], potion_id)
            entry["used"] = int(entry.get("used", 0)) + int(count)
        for modifier_id, count in metrics.get("modifiers_applied", {}).items():
            entry = self._entry(comp["card_modifiers"], modifier_id)
            entry["applied"] = int(entry.get("applied", 0)) + int(count)
        for modifier_id, count in metrics.get("modifiers_cleansed", {}).items():
            entry = self._entry(comp["card_modifiers"], modifier_id)
            entry["cleansed"] = int(entry.get("cleansed", 0)) + int(count)
        for ancient_id, count in metrics.get("ancients_seen", {}).items():
            self._entry(comp["ancients"], ancient_id)
        for key, count in metrics.get("ancient_choices", {}).items():
            ancient_id, choice_id = key.split(".", 1)
            entry = self._entry(comp["ancients"], ancient_id)
            choices = entry.setdefault("choices", {})
            choices[choice_id] = int(choices.get(choice_id, 0)) + int(count)

    def update_timeline_unlocks(self) -> list[str]:
        unlocked = set(self.profile.timeline.get("unlocked_fragments", []) or [])
        newly_unlocked: list[str] = []
        for fragment_id, item in self.registry.timeline_fragments.items():
            if fragment_id in unlocked:
                continue
            data = item.data
            conditions = data.get("unlock_conditions", []) or []
            if all(condition_met(self.profile, condition) for condition in conditions):
                unlocked.add(fragment_id)
                newly_unlocked.append(fragment_id)
        self.profile.timeline["unlocked_fragments"] = sorted(unlocked)
        return newly_unlocked
