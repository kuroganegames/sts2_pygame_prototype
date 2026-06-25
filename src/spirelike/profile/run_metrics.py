from __future__ import annotations

from datetime import datetime, timezone
import uuid


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunMetricsSystem:
    @staticmethod
    def ensure(run_state) -> dict:
        metrics = run_state.flags.get("run_metrics")
        if not isinstance(metrics, dict):
            metrics = {
                "run_id": uuid.uuid4().hex,
                "started_at": now_iso(),
                "enemies_seen": {},
                "enemies_defeated": {},
                "cards_seen": {},
                "cards_acquired": {},
                "cards_played": {},
                "cards_upgraded": {},
                "cards_removed": {},
                "cards_transformed": {},
                "relics_acquired": {},
                "potions_acquired": {},
                "potions_used": {},
                "modifiers_applied": {},
                "modifiers_cleansed": {},
                "ancients_seen": {},
                "ancient_choices": {},
                "nodes_visited": {},
                "gold_gained": 0,
            }
            run_state.flags["run_metrics"] = metrics
        return metrics

    @staticmethod
    def increment(run_state, bucket: str, item_id: str, amount: int = 1) -> None:
        metrics = RunMetricsSystem.ensure(run_state)
        data = metrics.setdefault(bucket, {})
        data[item_id] = int(data.get(item_id, 0)) + int(amount)

    @staticmethod
    def add_number(run_state, key: str, amount: int) -> None:
        metrics = RunMetricsSystem.ensure(run_state)
        metrics[key] = int(metrics.get(key, 0)) + int(amount)

    @staticmethod
    def record_enemy_seen(run_state, enemy_id: str) -> None:
        RunMetricsSystem.increment(run_state, "enemies_seen", enemy_id)

    @staticmethod
    def record_enemy_defeated(run_state, enemy_id: str) -> None:
        RunMetricsSystem.increment(run_state, "enemies_defeated", enemy_id)

    @staticmethod
    def record_card_seen(run_state, card_id: str) -> None:
        RunMetricsSystem.increment(run_state, "cards_seen", card_id)

    @staticmethod
    def record_card_acquired(run_state, card_id: str) -> None:
        RunMetricsSystem.increment(run_state, "cards_acquired", card_id)
        RunMetricsSystem.record_card_seen(run_state, card_id)

    @staticmethod
    def record_card_played(run_state, card_id: str) -> None:
        RunMetricsSystem.increment(run_state, "cards_played", card_id)
        RunMetricsSystem.record_card_seen(run_state, card_id)

    @staticmethod
    def record_card_upgraded(run_state, card_id: str) -> None:
        RunMetricsSystem.increment(run_state, "cards_upgraded", card_id)

    @staticmethod
    def record_card_removed(run_state, card_id: str) -> None:
        RunMetricsSystem.increment(run_state, "cards_removed", card_id)

    @staticmethod
    def record_card_transformed(run_state, old_card_id: str, new_card_id: str) -> None:
        RunMetricsSystem.increment(run_state, "cards_transformed", old_card_id)
        RunMetricsSystem.record_card_seen(run_state, new_card_id)

    @staticmethod
    def record_relic_acquired(run_state, relic_id: str) -> None:
        RunMetricsSystem.increment(run_state, "relics_acquired", relic_id)

    @staticmethod
    def record_potion_acquired(run_state, potion_id: str) -> None:
        RunMetricsSystem.increment(run_state, "potions_acquired", potion_id)

    @staticmethod
    def record_potion_used(run_state, potion_id: str) -> None:
        RunMetricsSystem.increment(run_state, "potions_used", potion_id)

    @staticmethod
    def record_modifier_applied(run_state, modifier_id: str) -> None:
        RunMetricsSystem.increment(run_state, "modifiers_applied", modifier_id)

    @staticmethod
    def record_modifier_cleansed(run_state, modifier_id: str) -> None:
        RunMetricsSystem.increment(run_state, "modifiers_cleansed", modifier_id)

    @staticmethod
    def record_ancient_seen(run_state, ancient_id: str) -> None:
        RunMetricsSystem.increment(run_state, "ancients_seen", ancient_id)

    @staticmethod
    def record_ancient_choice(run_state, ancient_id: str, choice_id: str) -> None:
        RunMetricsSystem.record_ancient_seen(run_state, ancient_id)
        RunMetricsSystem.increment(run_state, "ancient_choices", f"{ancient_id}.{choice_id}")
