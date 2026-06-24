from __future__ import annotations

import pygame

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import RunState
from spirelike.ui import colors
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.text import draw_text


class PotionBar:
    def __init__(self, registry: ContentRegistry, run_state: RunState, origin: tuple[int, int]) -> None:
        self.registry = registry
        self.run_state = run_state
        self.origin = origin
        self.slot_rects: dict[int, pygame.Rect] = {}

    def draw(self, surface) -> dict[int, pygame.Rect]:
        self.slot_rects.clear()
        x, y = self.origin
        draw_text(surface, "Potions", get_font(16, bold=True), colors.MUTED, (x, y - 22))
        for index, potion in enumerate(self.run_state.player.potions):
            rect = pygame.Rect(x + index * 72, y, 62, 62)
            self.slot_rects[index] = rect
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(surface, colors.PANEL_LIGHT if hovered else colors.PANEL, rect, border_radius=10)
            pygame.draw.rect(surface, colors.GOLD if hovered else (100, 105, 130), rect, width=2, border_radius=10)
            if potion is None:
                draw_text(surface, "空", get_font(18), colors.MUTED, rect.center, center=True)
                continue
            potion_def = self.registry.potion(potion.potion_id)
            image_path = self.registry.potions[potion.potion_id].image_path
            surface.blit(image_cache.load(image_path, (42, 42)), (rect.x + 10, rect.y + 6))
            name = str(potion_def.get("name", potion.potion_id))[:5]
            draw_text(surface, name, get_font(12), colors.TEXT, (rect.centerx, rect.bottom - 10), center=True)
        return self.slot_rects
