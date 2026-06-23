from __future__ import annotations

import pygame

from spirelike.core.run_factory import create_run
from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.text import draw_text, draw_wrapped


class CharacterSelectScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.character_rects: list[tuple[str, pygame.Rect]] = []
        self.buttons = [Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("title"))]
        self._layout()

    def _layout(self) -> None:
        start_x = 120
        y = 160
        gap = 40
        card_w, card_h = 280, 380
        for index, character_id in enumerate(self.app.registry.characters.keys()):
            rect = pygame.Rect(start_x + index * (card_w + gap), y, card_w, card_h)
            self.character_rects.append((character_id, rect))

    def handle_event(self, event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for character_id, rect in self.character_rects:
                if rect.collidepoint(event.pos):
                    self.start_run(character_id)

    def start_run(self, character_id: str) -> None:
        run = create_run(self.app.registry, character_id)
        self.app.run_state = run
        self.app.scene_manager.change("map", {"run_state": run})

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "キャラクター選択", get_font(44, bold=True), colors.TEXT, (640, 70), center=True)
        for character_id, rect in self.character_rects:
            character = self.app.registry.character(character_id)
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(surface, colors.PANEL_LIGHT if hovered else colors.PANEL, rect, border_radius=16)
            pygame.draw.rect(surface, colors.GOLD if hovered else colors.WHITE, rect, width=2, border_radius=16)
            image_path = self.app.registry.characters[character_id].image_path
            art_rect = pygame.Rect(rect.x + 40, rect.y + 28, rect.width - 80, 160)
            surface.blit(image_cache.load(image_path, art_rect.size), art_rect)
            draw_text(surface, character.get("name", character_id), get_font(28, bold=True), colors.GOLD, (rect.centerx, rect.y + 215), center=True)
            stats = f"HP {character.get('max_hp')} / Energy {character.get('base_energy')} / Gold {character.get('starting_gold')}"
            draw_text(surface, stats, get_font(18), colors.MUTED, (rect.centerx, rect.y + 255), center=True)
            desc_rect = pygame.Rect(rect.x + 24, rect.y + 290, rect.width - 48, 70)
            draw_wrapped(surface, character.get("description", ""), get_font(18), colors.TEXT, desc_rect)
        for button in self.buttons:
            button.draw(surface)
