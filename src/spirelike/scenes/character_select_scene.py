from __future__ import annotations

import pygame

from spirelike.core.run_factory import create_run
from spirelike.profile.run_metrics import RunMetricsSystem
from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.difficulty_system import DifficultySystem
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.text import draw_text, draw_wrapped


class CharacterSelectScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.save_slot_id = payload.get("save_slot_id", "slot_001")
        self.run_config = dict(payload.get("run_config") or {})
        self.difficulty_system = DifficultySystem(app.registry)
        self.selected_character_id = next(iter(app.registry.characters.keys()), None)
        self.difficulty_level = int(self.run_config.get("difficulty_level", 0))
        if self.selected_character_id:
            self.difficulty_level = min(self.difficulty_level, self.unlocked_difficulty_for(self.selected_character_id))
        self.character_rects: list[tuple[str, pygame.Rect]] = []
        self.buttons = [
            Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("run_setup", {"save_slot_id": self.save_slot_id, "run_config": self.run_config})),
            Button((430, 610, 54, 44), "<", self.prev_difficulty),
            Button((796, 610, 54, 44), ">", self.next_difficulty),
            Button((520, 610, 240, 44), "このキャラで開始", self.start_selected_run),
        ]
        self._layout()

    def _layout(self) -> None:
        start_x = 120
        y = 150
        gap = 40
        card_w, card_h = 280, 380
        for index, character_id in enumerate(self.app.registry.characters.keys()):
            rect = pygame.Rect(start_x + index * (card_w + gap), y, card_w, card_h)
            self.character_rects.append((character_id, rect))

    def unlocked_difficulty_for(self, character_id: str) -> int:
        stats = self.app.profile_system.profile.characters.get(character_id, {})
        return min(
            int(stats.get("highest_difficulty_unlocked", 0)),
            self.difficulty_system.max_defined_level(),
        )

    def select_character(self, character_id: str) -> None:
        self.selected_character_id = character_id
        self.difficulty_level = min(self.difficulty_level, self.unlocked_difficulty_for(character_id))

    def prev_difficulty(self) -> None:
        self.difficulty_level = max(0, self.difficulty_level - 1)

    def next_difficulty(self) -> None:
        if not self.selected_character_id:
            return
        unlocked = self.unlocked_difficulty_for(self.selected_character_id)
        self.difficulty_level = min(self.difficulty_level + 1, unlocked, self.difficulty_system.max_defined_level())

    def handle_event(self, event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for character_id, rect in self.character_rects:
                if rect.collidepoint(event.pos):
                    self.select_character(character_id)
                    return

    def start_selected_run(self) -> None:
        if not self.selected_character_id:
            return
        config = dict(self.run_config)
        config["difficulty_level"] = int(self.difficulty_level)
        run = create_run(self.app.registry, self.selected_character_id, run_config=config)
        run.flags["save_slot_id"] = self.save_slot_id
        RunMetricsSystem.ensure(run)
        self.app.profile_system.record_run_started(run)
        self.app.run_state = run
        self.app.scene_manager.change(
            "ancient",
            {"run_state": run, "after": "map", "phase": "run_start"},
        )

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "キャラクター選択", get_font(44, bold=True), colors.TEXT, (640, 60), center=True)
        mode = self.run_config.get("mode", "standard")
        draw_text(surface, f"保存先: {self.save_slot_id} / Mode: {mode} / Seed: {self.run_config.get('seed', '-')}", get_font(18), colors.MUTED, (640, 100), center=True)
        for character_id, rect in self.character_rects:
            character = self.app.registry.character(character_id)
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            selected = character_id == self.selected_character_id
            pygame.draw.rect(surface, colors.PANEL_LIGHT if hovered or selected else colors.PANEL, rect, border_radius=16)
            pygame.draw.rect(surface, colors.GOLD if selected or hovered else colors.WHITE, rect, width=3 if selected else 2, border_radius=16)
            image_path = self.app.registry.characters[character_id].image_path
            art_rect = pygame.Rect(rect.x + 40, rect.y + 28, rect.width - 80, 150)
            surface.blit(image_cache.load(image_path, art_rect.size), art_rect)
            draw_text(surface, character.get("name", character_id), get_font(28, bold=True), colors.GOLD, (rect.centerx, rect.y + 205), center=True)
            stats = f"HP {character.get('max_hp')} / Energy {character.get('base_energy')} / Gold {character.get('starting_gold')}"
            draw_text(surface, stats, get_font(17), colors.MUTED, (rect.centerx, rect.y + 245), center=True)
            unlocked = self.unlocked_difficulty_for(character_id)
            draw_text(surface, f"Difficulty解放: {unlocked}", get_font(15), colors.PURPLE, (rect.centerx, rect.y + 272), center=True)
            desc_rect = pygame.Rect(rect.x + 24, rect.y + 300, rect.width - 48, 58)
            draw_wrapped(surface, character.get("description", ""), get_font(17), colors.TEXT, desc_rect)

        difficulty_def = self.difficulty_system.level_def(self.difficulty_level) or {"name": "標準", "description": ""}
        draw_text(surface, f"Difficulty {self.difficulty_level}: {difficulty_def.get('name')}", get_font(24, bold=True), colors.GOLD, (640, 560), center=True)
        draw_text(surface, difficulty_def.get("description", ""), get_font(17), colors.TEXT, (640, 588), center=True)
        for button in self.buttons:
            button.draw(surface)
