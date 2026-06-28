from __future__ import annotations

import pygame

from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text, draw_wrapped


class AchievementScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.profile = app.profile_system.profile
        self.buttons = [Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("profile"))]

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "実績", get_font(44, bold=True), colors.GOLD, (640, 66), center=True)
        achievements = sorted(
            self.app.registry.achievements.items(),
            key=lambda item: (str(item[1].data.get("category", "general")), item[0]),
        )
        unlocked_count = sum(1 for achievement_id, _ in achievements if self.is_unlocked(achievement_id))
        draw_text(surface, f"解除済み: {unlocked_count} / {len(achievements)}", get_font(20), colors.MUTED, (640, 108), center=True)

        y = 145
        for achievement_id, item in achievements[:10]:
            data = item.data
            unlocked = self.is_unlocked(achievement_id)
            hidden = bool(data.get("hidden_until_unlocked", False)) and not unlocked
            rect = pygame.Rect(160, y, 960, 76)
            pygame.draw.rect(surface, colors.PANEL, rect, border_radius=10)
            pygame.draw.rect(surface, colors.GOLD if unlocked else colors.PANEL_LIGHT, rect, width=2, border_radius=10)
            if hidden:
                name = "???"
                description = "隠された実績"
            elif unlocked:
                name = data.get("name", achievement_id)
                description = data.get("description", "")
            else:
                name = data.get("name", achievement_id)
                description = data.get("locked_description", data.get("description", ""))
            marker = "解除済み" if unlocked else "未解除"
            draw_text(surface, f"[{marker}] {name}", get_font(21, bold=True), colors.GOLD if unlocked else colors.MUTED, (rect.x + 16, rect.y + 10))
            draw_wrapped(surface, description, get_font(16), colors.TEXT, pygame.Rect(rect.x + 16, rect.y + 40, rect.width - 32, 28))
            y += 88
        for button in self.buttons:
            button.draw(surface)

    def is_unlocked(self, achievement_id: str) -> bool:
        return bool(self.profile.achievements.get(achievement_id, {}).get("unlocked"))
