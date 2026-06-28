from __future__ import annotations

import pygame

from spirelike.models.entities import CardInstance
from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.card_reward_rarity_system import normalize_reward_card_choice
from spirelike.systems.reward_system import RewardBundle, RewardSystem
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.card_view import CardView
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.text import draw_text, draw_wrapped


class RewardScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload["run_state"]
        self.node_id = payload["node_id"]
        self.reward: RewardBundle = payload["reward"]
        self.after_boss = bool(payload.get("after_boss", False))
        self.reward_system = RewardSystem(app.registry)
        self.reward_system.apply_base_reward(self.run_state, self.reward)
        self.card_rects: dict[int, pygame.Rect] = {}
        self.buttons = [Button((550, 620, 180, 52), "スキップ/進む", self.finish)]

    def finish(self) -> None:
        self.run_state.map_state.mark_visited(self.node_id)
        if self.after_boss or self.run_state.map_state.boss_visited():
            self.app.scene_manager.change("run_result", {"run_state": self.run_state, "result": "victory"})
        else:
            self.app.scene_manager.change("map", {"run_state": self.run_state})

    def handle_event(self, event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in self.card_rects.items():
                if rect.collidepoint(event.pos):
                    if 0 <= index < len(self.reward.card_choices):
                        self.reward_system.choose_card(self.run_state, self.reward.card_choices[index])
                    self.reward.card_choices.clear()
                    self.finish()
                    return

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, self.reward.title, get_font(42, bold=True), colors.GOLD, (640, 60), center=True)
        y = 120
        if self.reward.gold:
            draw_text(surface, f"ゴールド +{self.reward.gold}", get_font(24), colors.TEXT, (640, y), center=True)
            y += 36
        if self.reward.relic_id:
            relic = self.app.registry.relic(self.reward.relic_id)
            box = pygame.Rect(420, y, 440, 96)
            pygame.draw.rect(surface, colors.PANEL, box, border_radius=12)
            image_path = self.app.registry.relics[self.reward.relic_id].image_path
            surface.blit(image_cache.load(image_path, (64, 64)), (box.x + 16, box.y + 16))
            draw_text(surface, relic.get("name", self.reward.relic_id), get_font(22, bold=True), colors.GOLD, (box.x + 94, box.y + 18))
            desc_rect = pygame.Rect(box.x + 94, box.y + 48, box.width - 110, 42)
            draw_wrapped(surface, relic.get("description", ""), get_font(15), colors.TEXT, desc_rect)
            y += 110
        if self.reward.potion_id:
            potion = self.app.registry.potion(self.reward.potion_id)
            box = pygame.Rect(420, y, 440, 76)
            pygame.draw.rect(surface, colors.PANEL, box, border_radius=12)
            image_path = self.app.registry.potions[self.reward.potion_id].image_path
            surface.blit(image_cache.load(image_path, (50, 50)), (box.x + 20, box.y + 13))
            draw_text(surface, f"ポーション: {potion.get('name', self.reward.potion_id)}", get_font(22, bold=True), colors.GOLD, (box.x + 90, box.y + 16))
            draw_text(surface, potion.get("description", ""), get_font(15), colors.TEXT, (box.x + 90, box.y + 44))
            y += 88
        if self.reward.message:
            draw_text(surface, self.reward.message, get_font(20), colors.MUTED, (640, y), center=True)
            y += 38

        self.card_rects.clear()
        choices = self.reward.card_choices
        if choices:
            draw_text(surface, "カードを1枚選択", get_font(26, bold=True), colors.TEXT, (640, 285), center=True)
            card_w, card_h = 160, 222
            total_w = len(choices) * (card_w + 24) - 24
            start_x = (1280 - total_w) // 2
            mouse = pygame.mouse.get_pos()
            for i, choice in enumerate(choices):
                normalized = normalize_reward_card_choice(choice)
                rect = pygame.Rect(start_x + i * (card_w + 24), 330, card_w, card_h)
                self.card_rects[i] = rect
                view = CardView(
                    self.app.registry,
                    rect,
                    CardInstance(card_id=normalized.card_id, upgraded=normalized.upgraded),
                )
                view.handle_motion(mouse)
                view.draw(surface)
        for button in self.buttons:
            button.draw(surface)
