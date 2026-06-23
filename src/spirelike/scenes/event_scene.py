from __future__ import annotations

import pygame

from spirelike.core.rng import RunRng
from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.run_effects import RunEffectExecutor
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.text import draw_text, draw_wrapped


class EventScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload["run_state"]
        self.node_id = payload["node_id"]
        rngs = RunRng(self.run_state.seed + self.run_state.floor)
        candidates = [item.data for item in app.registry.events.values() if self.run_state.act in (item.data.get("act_pool", []) or [self.run_state.act])]
        self.event_def = rngs.event.choice(candidates) if candidates else {"name": "静かな部屋", "description": "何も起こらなかった。", "choices": [{"text": "進む", "effects": []}]}
        self.executor = RunEffectExecutor(app.registry, rngs.event)
        self.buttons = []
        self._build_buttons()

    def _build_buttons(self) -> None:
        choices = self.event_def.get("choices", []) or []
        y = 430
        for i, choice in enumerate(choices):
            def make_callback(ch=choice):
                return lambda: self.choose(ch)
            self.buttons.append(Button((320, y + i * 68, 640, 52), choice.get("text", choice.get("name", "選択")), make_callback()))

    def choose(self, choice: dict) -> None:
        self.executor.execute_many(self.run_state, choice.get("effects", []))
        self.run_state.map_state.mark_visited(self.node_id)
        self.app.scene_manager.change("map", {"run_state": self.run_state})

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, self.event_def.get("name", "イベント"), get_font(40, bold=True), colors.GOLD, (640, 70), center=True)
        image_name = self.event_def.get("id")
        image_path = None
        if image_name and image_name in self.app.registry.events:
            image_path = self.app.registry.events[image_name].image_path
        art_rect = pygame.Rect(520, 125, 240, 150)
        surface.blit(image_cache.load(image_path, art_rect.size), art_rect)
        desc_rect = pygame.Rect(290, 310, 700, 90)
        draw_wrapped(surface, self.event_def.get("description", ""), get_font(22), colors.TEXT, desc_rect)
        for button in self.buttons:
            button.draw(surface)
