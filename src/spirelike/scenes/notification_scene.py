from __future__ import annotations

import pygame

from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.notification_system import NotificationSystem
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text, draw_wrapped


class NotificationScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.profile = app.profile_system.profile
        self.notification_system = NotificationSystem()
        self.notification_system.mark_all_seen(self.profile)
        app.profile_system.save()
        self.buttons = [Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("profile"))]

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "通知", get_font(44, bold=True), colors.GOLD, (640, 66), center=True)
        notifications = self.profile.notifications[:12]
        if not notifications:
            draw_text(surface, "通知はありません。", get_font(24), colors.MUTED, (640, 280), center=True)
        y = 125
        for notification in notifications:
            rect = pygame.Rect(165, y, 950, 68)
            pygame.draw.rect(surface, colors.PANEL, rect, border_radius=10)
            pygame.draw.rect(surface, colors.PANEL_LIGHT, rect, width=1, border_radius=10)
            title = notification.get("title", notification.get("type", "通知"))
            message = notification.get("message", "")
            created_at = str(notification.get("created_at", ""))[:19].replace("T", " ")
            draw_text(surface, title, get_font(19, bold=True), colors.GOLD, (rect.x + 14, rect.y + 8))
            draw_text(surface, created_at, get_font(13), colors.MUTED, (rect.right - 190, rect.y + 12))
            draw_wrapped(surface, message, get_font(15), colors.TEXT, pygame.Rect(rect.x + 14, rect.y + 36, rect.width - 28, 24))
            y += 78
        for button in self.buttons:
            button.draw(surface)
