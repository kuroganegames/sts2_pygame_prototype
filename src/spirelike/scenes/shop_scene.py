from __future__ import annotations

import pygame

from spirelike.core.rng import RunRng
from spirelike.models.entities import CardInstance
from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.potion_system import PotionSystem
from spirelike.systems.shop_system import ShopSystem
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.card_view import CardView
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.text import draw_text


class ShopScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload["run_state"]
        self.node_id = payload["node_id"]
        rngs = RunRng(self.run_state.seed + self.run_state.floor)
        self.shop_system = ShopSystem(app.registry)
        self.potion_system = PotionSystem(app.registry)
        self.offers = self.shop_system.generate_card_offers(self.run_state, rngs.shop, count=5)
        self.potion_offers = self.shop_system.generate_potion_offers(rngs.shop, count=3)
        self.card_rects: dict[int, pygame.Rect] = {}
        self.potion_rects: dict[int, pygame.Rect] = {}
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
            for i, rect in self.potion_rects.items():
                if rect.collidepoint(event.pos):
                    offer = self.potion_offers[i]
                    if not offer.sold and self.run_state.player.gold >= offer.price:
                        if self.potion_system.grant_potion(self.run_state, offer.potion_id):
                            self.run_state.player.gold -= offer.price
                            offer.sold = True
                    return

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "ショップ", get_font(42, bold=True), colors.GOLD, (640, 50), center=True)
        draw_text(surface, f"Gold {self.run_state.player.gold}", get_font(24), colors.TEXT, (640, 96), center=True)
        self.card_rects.clear()
        card_w, card_h = 145, 202
        start_x = 150
        mouse = pygame.mouse.get_pos()
        draw_text(surface, "カード", get_font(24, bold=True), colors.TEXT, (80, 160))
        for i, offer in enumerate(self.offers):
            rect = pygame.Rect(start_x + i * 190, 150, card_w, card_h)
            self.card_rects[i] = rect
            enabled = not offer.sold and self.run_state.player.gold >= offer.price
            view = CardView(self.app.registry, rect, offer.card_id, enabled=enabled)
            view.handle_motion(mouse)
            view.draw(surface)
            price_text = "売切" if offer.sold else f"{offer.price}G"
            draw_text(surface, price_text, get_font(20, bold=True), colors.GOLD, (rect.centerx, rect.bottom + 24), center=True)

        draw_text(surface, "ポーション", get_font(24, bold=True), colors.TEXT, (80, 430))
        self.potion_rects.clear()
        for i, offer in enumerate(self.potion_offers):
            rect = pygame.Rect(230 + i * 260, 425, 220, 82)
            self.potion_rects[i] = rect
            enabled = not offer.sold and self.run_state.player.gold >= offer.price and self.potion_system.has_empty_slot(self.run_state)
            pygame.draw.rect(surface, colors.PANEL_LIGHT if enabled else (55, 55, 64), rect, border_radius=12)
            pygame.draw.rect(surface, colors.GOLD if enabled else colors.MUTED, rect, width=2, border_radius=12)
            potion = self.app.registry.potion(offer.potion_id)
            image_path = self.app.registry.potions[offer.potion_id].image_path
            surface.blit(image_cache.load(image_path, (52, 52)), (rect.x + 12, rect.y + 14))
            draw_text(surface, potion.get("name", offer.potion_id), get_font(18, bold=True), colors.TEXT, (rect.x + 76, rect.y + 13))
            price_text = "売切" if offer.sold else f"{offer.price}G"
            draw_text(surface, price_text, get_font(18, bold=True), colors.GOLD, (rect.x + 76, rect.y + 45))
        for button in self.buttons:
            button.draw(surface)
