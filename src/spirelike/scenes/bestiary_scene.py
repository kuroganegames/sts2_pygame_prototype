from __future__ import annotations

import pygame

from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.text import draw_text


class BestiaryScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.profile = app.profile_system.profile
        self.buttons = [Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("profile"))]

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "敵図鑑", get_font(44, bold=True), colors.GOLD, (640, 70), center=True)
        x, y = 110, 130
        for index, (enemy_id, item) in enumerate(self.app.registry.enemies.items()):
            entry = self.profile.bestiary.get(enemy_id, {})
            seen = bool(entry.get("seen"))
            rect = pygame.Rect(x + (index % 3) * 360, y + (index // 3) * 130, 320, 105)
            pygame.draw.rect(surface, colors.PANEL, rect, border_radius=10)
            pygame.draw.rect(surface, colors.PANEL_LIGHT, rect, width=1, border_radius=10)
            if seen:
                surface.blit(image_cache.load(item.image_path, (64, 64)), (rect.x + 14, rect.y + 18))
                name = item.data.get("name", enemy_id)
                lines = [
                    name,
                    f"遭遇: {entry.get('encountered', 0)}",
                    f"撃破: {entry.get('defeated', 0)}",
                ]
            else:
                lines = ["???", "未発見"]
            draw_text(surface, lines[0], get_font(20, bold=True), colors.GOLD if seen else colors.MUTED, (rect.x + 90, rect.y + 16))
            for i, line in enumerate(lines[1:]):
                draw_text(surface, line, get_font(16), colors.TEXT, (rect.x + 90, rect.y + 46 + i * 22))
        for button in self.buttons:
            button.draw(surface)
