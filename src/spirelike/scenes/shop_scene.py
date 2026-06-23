from __future__ import annotations

import pygame

from spirelike.core.rng import RunRng
from spirelike.models.entities import CardInstance
from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.shop_system import ShopOffer, ShopSystem
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.card_view import CardView
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class ShopScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload["run_state"]
        self.node_id = payload["node_id"]
        rngs = RunRng(self.run_state.seed + self.run_state.floor)
        self.offers = ShopSystem(app.registry).generate_card_offers(self.run_state, rngs.shop, count=5)
        self.card_rects: dict[int, pygame.Rect] = {}
        self.buttons = [Button((540, 620, 200, 52), "店を出る", self.finish)]

    def finish(self) -> None:
        self.run_state.map_state.mark_visited(self.node_id)
        self.app.scene_manager.change("map", {"run_state": self.run_state})

    def handle_event(self, event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in self.card_rects.items():
                if rect.collidepoint(event.pos):
                    offer = self.offers[i]
                    if not offer.sold and self.run_state.player.gold >= offer.price:
                        self.run_state.player.gold -= offer.price
                        self.run_state.player.deck.append(CardInstance(card_id=offer.card_id))
                        offer.sold = True
                        self.run_state.add_message(f"購入: {self.app.registry.card(offer.card_id).get('name', offer.card_id)}")
                    return

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "ショップ", get_font(42, bold=True), colors.GOLD, (640, 70), center=True)
        draw_text(surface, f"Gold {self.run_state.player.gold}", get_font(24), colors.TEXT, (640, 120), center=True)
        self.card_rects.clear()
        card_w, card_h = 150, 210
        start_x = 130
        mouse = pygame.mouse.get_pos()
        for i, offer in enumerate(self.offers):
            rect = pygame.Rect(start_x + i * 205, 215, card_w, card_h)
            self.card_rects[i] = rect
            view = CardView(self.app.registry, rect, offer.card_id, enabled=(not offer.sold and self.run_state.player.gold >= offer.price))
            view.handle_motion(mouse)
            view.draw(surface)
            price_text = "売切" if offer.sold else f"{offer.price}G"
            draw_text(surface, price_text, get_font(22, bold=True), colors.GOLD, (rect.centerx, rect.bottom + 28), center=True)
        for button in self.buttons:
            button.draw(surface)
