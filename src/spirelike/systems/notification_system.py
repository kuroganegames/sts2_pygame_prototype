from __future__ import annotations

from typing import Any

from spirelike.profile.profile_data import ProfileState
from spirelike.profile.run_metrics import now_iso


class NotificationSystem:
    MAX_NOTIFICATIONS = 100

    def add_notification(
        self,
        profile: ProfileState,
        *,
        notification_id: str,
        notification_type: str,
        title: str,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        profile.ensure_defaults()
        if any(item.get("notification_id") == notification_id for item in profile.notifications):
            return None
        notification = {
            "notification_id": notification_id,
            "type": notification_type,
            "title": title,
            "message": message,
            "created_at": now_iso(),
            "seen": False,
            "payload": dict(payload or {}),
        }
        profile.notifications.insert(0, notification)
        profile.notifications = profile.notifications[: self.MAX_NOTIFICATIONS]
        return notification

    def mark_all_seen(self, profile: ProfileState) -> None:
        profile.ensure_defaults()
        for item in profile.notifications:
            item["seen"] = True

    def unread_count(self, profile: ProfileState) -> int:
        profile.ensure_defaults()
        return sum(1 for item in profile.notifications if not item.get("seen"))
