from __future__ import annotations

import pygame

from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class RestScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload["run_state"]
        self.node_id = payload["node_id"]
        self.buttons = [
            Button((430, 250, 200, 70), "休憩: 30%回復", self.rest),
            Button((650, 250, 200, 70), "鍛冶: 1枚強化", self.upgrade),
            Button((540, 600, 200, 52), "戻る", self.finish),
        ]
        self.card_rects: list[tuple[int, pygame.Rect]] = []
        self.choosing_upgrade = False

    def rest(self) -> None:
        amount = int(self.run_state.player.max_hp * 0.30)
        healed = self.run_state.player.heal(amount)
        self.run_state.add_message(f"休憩: HPを{healed}回復")
        self.finish()

    def upgrade(self) -> None:
        self.choosing_upgrade = True
        self.run_state.add_message("強化するカードを選択")

    def finish(self) -> None:
        self.run_state.map_state.mark_visited(self.node_id)
        self.app.scene_manager.change("map", {"run_state": self.run_state})

    def handle_event(self, event) -> None:
        super().handle_event(event)
        if self.choosing_upgrade and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in self.card_rects:
                if rect.collidepoint(event.pos):
                    card = self.run_state.player.deck[index]
                    if not card.upgraded and self.app.registry.card(card.card_id).get("upgrade"):
                        card.upgraded = True
                        self.run_state.add_message(f"強化: {self.app.registry.card_display_name(card.card_id, True)}")
                        self.finish()
                    return

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "休憩所", get_font(42, bold=True), colors.GOLD, (640, 70), center=True)
        p = self.run_state.player
        draw_text(surface, f"HP {p.hp}/{p.max_hp}", get_font(24), colors.TEXT, (640, 130), center=True)
        if not self.choosing_upgrade:
            for button in self.buttons:
                button.draw(surface)
        else:
            draw_text(surface, "強化するカードを選んでください", get_font(24), colors.TEXT, (640, 185), center=True)
            self.card_rects.clear()
            x, y = 170, 240
            for i, card in enumerate(self.run_state.player.deck[:28]):
                rect = pygame.Rect(x + (i % 7) * 135, y + (i // 7) * 70, 120, 52)
                self.card_rects.append((i, rect))
                can = not card.upgraded and bool(self.app.registry.card(card.card_id).get("upgrade"))
                pygame.draw.rect(surface, colors.PANEL_LIGHT if can else (55, 55, 62), rect, border_radius=8)
                pygame.draw.rect(surface, colors.GOLD if can else colors.MUTED, rect, width=1, border_radius=8)
                draw_text(surface, self.app.registry.card_display_name(card.card_id, card.upgraded), get_font(15), colors.TEXT, rect.center, center=True)
