from __future__ import annotations

import pygame

from spirelike.ui import colors
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class Button:
    def __init__(self, rect, text: str, callback, *, enabled: bool = True) -> None:
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.enabled = enabled
        self.hovered = False

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.enabled and self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

    def draw(self, surface) -> None:
        if not self.enabled:
            fill = (64, 64, 72)
            border = (90, 90, 100)
        elif self.hovered:
            fill = colors.PANEL_LIGHT
            border = colors.GOLD
        else:
            fill = colors.PANEL
            border = (100, 105, 130)
        pygame.draw.rect(surface, fill, self.rect, border_radius=10)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=10)
        draw_text(surface, self.text, get_font(22, bold=True), colors.TEXT, self.rect.center, center=True)
