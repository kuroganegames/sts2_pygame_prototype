from __future__ import annotations

import pygame

from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text, draw_wrapped


class TimelineScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.profile = app.profile_system.profile
        self.buttons = [Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("profile"))]

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "Timeline", get_font(44, bold=True), colors.GOLD, (640, 65), center=True)
        unlocked = set(self.profile.timeline.get("unlocked_fragments", []) or [])
        fragments = sorted(
            self.app.registry.timeline_fragments.items(),
            key=lambda item: (int(item[1].data.get("order", 999)), item[0]),
        )
        y = 130
        for fragment_id, item in fragments:
            data = item.data
            is_unlocked = fragment_id in unlocked
            rect = pygame.Rect(170, y, 940, 92)
            pygame.draw.rect(surface, colors.PANEL, rect, border_radius=10)
            pygame.draw.rect(surface, colors.GOLD if is_unlocked else colors.PANEL_LIGHT, rect, width=2, border_radius=10)
            title = data.get("title", fragment_id) if is_unlocked else "???"
            desc = data.get("description", "") if is_unlocked else "未解放の断片"
            draw_text(surface, title, get_font(22, bold=True), colors.GOLD if is_unlocked else colors.MUTED, (rect.x + 18, rect.y + 10))
            draw_wrapped(surface, desc, get_font(17), colors.TEXT, pygame.Rect(rect.x + 18, rect.y + 42, rect.width - 36, 42))
            y += 108
        for button in self.buttons:
            button.draw(surface)
