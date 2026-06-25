from __future__ import annotations

import pygame

from spirelike.core.rng import RunRng
from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.ancient_system import AncientSystem
from spirelike.systems.run_effects import RunEffectExecutor
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.text import draw_text, draw_wrapped


class AncientScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload["run_state"]
        self.node_id = payload.get("node_id")
        self.after = payload.get("after", "map")
        self.phase = payload.get("phase", "node")
        rngs = RunRng(self.run_state.seed + self.run_state.floor + len(self.run_state.ancient_blessings) * 997)
        self.rng = rngs.event
        self.ancient_system = AncientSystem(app.registry)
        self.executor = RunEffectExecutor(app.registry, self.rng)
        self.ancient_def = self.ancient_system.choose_ancient(self.run_state, self.rng)
        self.choice_rects: list[tuple[dict, pygame.Rect]] = []
        self.buttons = []
        if self.ancient_def is None:
            self.buttons = [Button((540, 560, 200, 54), "進む", self.finish)]

    def finish(self) -> None:
        if self.node_id:
            self.run_state.map_state.mark_visited(self.node_id)
        self.app.scene_manager.change(self.after, {"run_state": self.run_state})

    def handle_event(self, event) -> None:
        super().handle_event(event)
        if self.ancient_def and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for choice, rect in self.choice_rects:
                if rect.collidepoint(event.pos):
                    self.ancient_system.apply_choice(self.run_state, self.ancient_def, choice, self.executor)
                    if self.run_state.pending_selection is not None:
                        self.app.scene_manager.change(
                            "card_select",
                            {
                                "run_state": self.run_state,
                                "request": self.run_state.pending_selection,
                                "return_scene": self.after,
                                "return_payload": {"run_state": self.run_state},
                                "finish_node_id": self.node_id,
                            },
                        )
                        return
                    self.finish()
                    return

    def draw(self, surface) -> None:
        surface.fill((20, 22, 30))
        if self.ancient_def is None:
            draw_text(surface, "静寂", get_font(46, bold=True), colors.GOLD, (640, 160), center=True)
            draw_text(surface, "この層に呼びかける存在はいない。", get_font(24), colors.TEXT, (640, 240), center=True)
            for button in self.buttons:
                button.draw(surface)
            return

        ancient = self.ancient_def
        ancient_id = ancient.get("id")
        draw_text(surface, ancient.get("name", ancient_id), get_font(44, bold=True), colors.GOLD, (640, 56), center=True)
        phase_text = "ラン開始時の祝福" if self.phase == "run_start" else "エンシェント"
        draw_text(surface, phase_text, get_font(18), colors.MUTED, (640, 98), center=True)

        image_path = None
        if ancient_id in self.app.registry.ancients:
            image_path = self.app.registry.ancients[ancient_id].image_path
        art_rect = pygame.Rect(500, 120, 280, 165)
        surface.blit(image_cache.load(image_path, art_rect.size), art_rect)
        pygame.draw.rect(surface, colors.GOLD, art_rect, width=2)

        desc_rect = pygame.Rect(270, 305, 740, 82)
        draw_wrapped(surface, ancient.get("description", ""), get_font(22), colors.TEXT, desc_rect)

        self.choice_rects.clear()
        choices = ancient.get("choices", []) or []
        start_y = 420
        for index, choice in enumerate(choices):
            rect = pygame.Rect(240, start_y + index * 82, 800, 66)
            self.choice_rects.append((choice, rect))
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(surface, colors.PANEL_LIGHT if hovered else colors.PANEL, rect, border_radius=12)
            pygame.draw.rect(surface, colors.GOLD if hovered else (105, 110, 135), rect, width=2, border_radius=12)
            draw_text(surface, choice.get("name", choice.get("id", "選択")), get_font(22, bold=True), colors.GOLD, (rect.x + 18, rect.y + 8))
            draw_text(surface, choice.get("description", ""), get_font(17), colors.TEXT, (rect.x + 18, rect.y + 36))
