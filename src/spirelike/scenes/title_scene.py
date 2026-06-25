from __future__ import annotations

import pygame

from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text, draw_wrapped


class TitleScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        w, h = app.settings.screen_width, app.settings.screen_height
        has_save = app.save_system.save_exists()
        self.buttons = [
            Button((w // 2 - 140, h // 2 + 30, 280, 54), "ラン開始", self.start),
            Button((w // 2 - 140, h // 2 + 96, 280, 54), "続きから", self.continue_run, enabled=has_save),
            Button((w // 2 - 140, h // 2 + 162, 280, 54), "プロフィール", self.profile),
            Button((w // 2 - 140, h // 2 + 228, 280, 54), "終了", self.app.quit),
        ]

    def start(self) -> None:
        self.app.scene_manager.change("character_select")

    def continue_run(self) -> None:
        self.app.continue_saved_run()

    def profile(self) -> None:
        self.app.scene_manager.change("profile")

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        w, h = self.app.settings.screen_width, self.app.settings.screen_height
        draw_text(surface, "SPIRELIKE", get_font(72, bold=True), colors.GOLD, (w // 2, 145), center=True)
        draw_text(surface, "Pygame / YAML-driven Deckbuilder Prototype", get_font(24), colors.MUTED, (w // 2, 215), center=True)
        rect = pygame.Rect(w // 2 - 330, 260, 660, 86)
        draw_wrapped(
            surface,
            "カード・敵・レリック・キャラ・マップ生成ルールをYAMLで差し替えられる初期実装です。",
            get_font(22),
            colors.TEXT,
            rect,
        )
        if self.app.last_load_error:
            draw_text(surface, f"ロード失敗: {self.app.last_load_error}", get_font(18), colors.RED, (w // 2, h // 2 + 292), center=True)
        for button in self.buttons:
            button.draw(surface)
