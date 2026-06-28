from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spirelike.profile.profile_data import ProfileState
from spirelike.systems.notification_system import NotificationSystem

profile = ProfileState()
profile.ensure_defaults()
system = NotificationSystem()
created = system.add_notification(
    profile,
    notification_id="achievement:first_victory",
    notification_type="achievement_unlocked",
    title="実績解除",
    message="テスト",
)
assert created is not None
assert system.unread_count(profile) == 1
assert system.add_notification(
    profile,
    notification_id="achievement:first_victory",
    notification_type="achievement_unlocked",
    title="重複",
    message="重複",
) is None
assert len(profile.notifications) == 1
system.mark_all_seen(profile)
assert system.unread_count(profile) == 0
for i in range(150):
    system.add_notification(
        profile,
        notification_id=f"test:{i}",
        notification_type="test",
        title=f"通知{i}",
        message="",
    )
assert len(profile.notifications) == system.MAX_NOTIFICATIONS
print("OK")
