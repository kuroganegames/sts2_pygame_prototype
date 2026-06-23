from __future__ import annotations

import pygame

from spirelike.content.loader import ContentRegistry
from spirelike.models.entities import CardInstance
from spirelike.ui import colors
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.text import draw_text, draw_wrapped


CARD_TYPE_COLORS = {
    "attack": (74, 48, 46),
    "skill": (44, 58, 74),
    "power": (58, 46, 74),
    "status": (65, 65, 65),
    "curse": (55, 42, 63),
}


class CardView:
    def __init__(self, registry: ContentRegistry, rect, card: CardInstance | str, *, enabled: bool = True) -> None:
        self.registry = registry
        self.rect = pygame.Rect(rect)
        if isinstance(card, str):
            self.card = CardInstance(card_id=card)
        else:
            self.card = card
        self.enabled = enabled
        self.hovered = False

    def handle_motion(self, pos) -> None:
        self.hovered = self.rect.collidepoint(pos)

    def draw(self, surface) -> None:
        card_def = self.registry.card(self.card.card_id)
        card_type = card_def.get("type", "skill")
        fill = CARD_TYPE_COLORS.get(card_type, colors.PANEL)
        if not self.enabled:
            fill = tuple(max(0, c - 25) for c in fill)
        rect = self.rect.copy()
        if self.hovered and self.enabled:
            rect.y -= 12
        pygame.draw.rect(surface, fill, rect, border_radius=12)
        pygame.draw.rect(surface, colors.GOLD if self.hovered else colors.WHITE, rect, width=2, border_radius=12)

        cost = self.registry.card_cost(self.card.card_id, self.card.upgraded)
        cost_rect = pygame.Rect(rect.x + 8, rect.y + 8, 30, 30)
        pygame.draw.ellipse(surface, colors.BLUE, cost_rect)
        draw_text(surface, cost, get_font(18, bold=True), colors.WHITE, cost_rect.center, center=True)

        name = self.registry.card_display_name(self.card.card_id, self.card.upgraded)
        draw_text(surface, name, get_font(17, bold=True), colors.TEXT, (rect.x + 44, rect.y + 10))

        image_path = self.registry.cards[self.card.card_id].image_path
        art_rect = pygame.Rect(rect.x + 12, rect.y + 44, rect.width - 24, 68)
        art = image_cache.load(image_path, art_rect.size)
        surface.blit(art, art_rect)
        pygame.draw.rect(surface, colors.BLACK, art_rect, width=1)

        type_text = str(card_type).upper()
        draw_text(surface, type_text, get_font(13, bold=True), colors.MUTED, (rect.x + 12, rect.y + 118))

        desc = self.registry.card_description(self.card.card_id, self.card.upgraded)
        desc_rect = pygame.Rect(rect.x + 12, rect.y + 138, rect.width - 24, rect.height - 146)
        draw_wrapped(surface, desc, get_font(13), colors.TEXT, desc_rect)

        if self.card.modifiers:
            mod_text = "+".join(self.card.modifiers)
            draw_text(surface, mod_text, get_font(11), colors.GOLD, (rect.x + 10, rect.bottom - 18))
