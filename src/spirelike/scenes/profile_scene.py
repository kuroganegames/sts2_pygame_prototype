from __future__ import annotations

from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.notification_system import NotificationSystem
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class ProfileScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.profile = app.profile_system.profile
        unread = NotificationSystem().unread_count(self.profile)
        notification_label = f"通知 ({unread})" if unread else "通知"
        self.buttons = [
            Button((380, 390, 210, 42), "ラン履歴", lambda: app.scene_manager.change("run_history")),
            Button((610, 390, 210, 42), "敵図鑑", lambda: app.scene_manager.change("bestiary")),
            Button((380, 442, 210, 42), "コレクション", lambda: app.scene_manager.change("compendium")),
            Button((610, 442, 210, 42), "Timeline", lambda: app.scene_manager.change("timeline")),
            Button((380, 494, 210, 42), "実績", lambda: app.scene_manager.change("achievements")),
            Button((610, 494, 210, 42), notification_label, lambda: app.scene_manager.change("notifications")),
            Button((495, 546, 210, 42), "解放ツリー", lambda: app.scene_manager.change("unlock_tree")),
            Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("title")),
        ]

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        summary = self.profile.summary
        compendium = self.profile.compendium
        achievements_unlocked = sum(1 for entry in self.profile.achievements.values() if entry.get("unlocked"))
        draw_text(surface, "プロフィール", get_font(44, bold=True), colors.GOLD, (640, 70), center=True)
        lines = [
            f"総ラン数: {summary.get('runs_started', 0)}",
            f"完了ラン: {summary.get('runs_completed', 0)}",
            f"勝利: {summary.get('victories', 0)} / 敗北: {summary.get('defeats', 0)}",
            f"最高到達階: {summary.get('highest_floor', 0)} / Act {summary.get('highest_act', 0)}",
            f"倒した敵: {summary.get('total_enemies_defeated', 0)}",
            f"見つけたカード: {len(compendium.get('cards', {}))} / {len(self.app.registry.cards)}",
            f"見つけたレリック: {len(compendium.get('relics', {}))} / {len(self.app.registry.relics)}",
            f"Timeline: {len(self.profile.timeline.get('unlocked_fragments', []))} / {len(self.app.registry.timeline_fragments)}",
            f"実績: {achievements_unlocked} / {len(self.app.registry.achievements)}",
        ]
        y = 125
        for line in lines:
            draw_text(surface, line, get_font(23), colors.TEXT, (440, y))
            y += 29
        for button in self.buttons:
            button.draw(surface)
