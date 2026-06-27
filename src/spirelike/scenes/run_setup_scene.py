from __future__ import annotations

import pygame

from spirelike.core.seed_utils import random_seed, seed_from_text
from spirelike.models.run_config import RunConfig, run_config_to_dict
from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text, draw_wrapped


class RunSetupScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.save_slot_id = payload.get("save_slot_id", "slot_001")
        existing_config = payload.get("run_config") or {}
        self.seed_text = str(existing_config.get("seed", random_seed()))
        self.custom_enabled = bool(existing_config.get("custom", False))
        self.selected_modifiers: set[str] = set(existing_config.get("selected_modifiers", []) or [])
        self.seed_active = False
        self.error_message = ""
        self.seed_rect = pygame.Rect(410, 165, 300, 42)
        self.modifier_rects: dict[str, pygame.Rect] = {}
        self.buttons = [
            Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("save_slot", {"mode": "new"})),
            Button((730, 165, 140, 42), "ランダム", self.randomize_seed),
            Button((410, 230, 150, 44), "標準", self.set_standard),
            Button((580, 230, 150, 44), "カスタム", self.set_custom),
            Button((500, 625, 280, 52), "キャラクター選択へ", self.go_next),
        ]

    def randomize_seed(self) -> None:
        self.seed_text = str(random_seed())
        self.error_message = ""

    def set_standard(self) -> None:
        self.custom_enabled = False
        self.error_message = "標準ランではModifierは無効です。"

    def set_custom(self) -> None:
        self.custom_enabled = True
        self.error_message = "カスタムランはプロフィール集計対象外です。"

    def unlocked_run_modifiers(self) -> set[str]:
        profile = self.app.profile_system.profile
        return set(self.app.unlock_system.build_unlocked_snapshot(profile).get("run_modifiers", []))

    def build_run_config(self) -> RunConfig:
        seed = seed_from_text(self.seed_text)
        unlocked = self.unlocked_run_modifiers()
        selected = sorted(modifier_id for modifier_id in self.selected_modifiers if modifier_id in unlocked)
        has_custom_modifiers = self.custom_enabled and bool(selected)
        mode = "custom" if self.custom_enabled else "seeded"
        return RunConfig(
            mode=mode,
            seed=seed,
            custom=self.custom_enabled,
            selected_modifiers=selected if self.custom_enabled else [],
            profile_eligible=not has_custom_modifiers and not self.custom_enabled,
            metadata={"seed_text": self.seed_text},
        )

    def go_next(self) -> None:
        try:
            config = self.build_run_config()
        except Exception as exc:
            self.error_message = f"Seedが不正です: {exc}"
            return
        self.app.scene_manager.change(
            "character_select",
            {
                "save_slot_id": self.save_slot_id,
                "run_config": run_config_to_dict(config),
            },
        )

    def handle_event(self, event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.seed_active = self.seed_rect.collidepoint(event.pos)
            profile = self.app.profile_system.profile
            for modifier_id, rect in self.modifier_rects.items():
                if rect.collidepoint(event.pos):
                    if not self.app.unlock_system.is_unlocked(profile, "run_modifier", modifier_id):
                        self.error_message = "このRun Modifierは未解放です。"
                        return
                    self.custom_enabled = True
                    if modifier_id in self.selected_modifiers:
                        self.selected_modifiers.remove(modifier_id)
                    else:
                        self.selected_modifiers.add(modifier_id)
                    self.error_message = "カスタムランはプロフィール集計対象外です。"
                    return
        if event.type == pygame.KEYDOWN and self.seed_active:
            if event.key == pygame.K_BACKSPACE:
                self.seed_text = self.seed_text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.go_next()
            elif event.unicode and event.unicode.isprintable() and len(self.seed_text) < 32:
                self.seed_text += event.unicode

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "ラン設定", get_font(44, bold=True), colors.GOLD, (640, 58), center=True)
        draw_text(surface, f"保存先: {self.save_slot_id}", get_font(18), colors.MUTED, (640, 98), center=True)

        draw_text(surface, "Seed", get_font(24, bold=True), colors.TEXT, (330, 174))
        pygame.draw.rect(surface, colors.PANEL_LIGHT if self.seed_active else colors.PANEL, self.seed_rect, border_radius=8)
        pygame.draw.rect(surface, colors.GOLD if self.seed_active else colors.MUTED, self.seed_rect, width=2, border_radius=8)
        draw_text(surface, self.seed_text, get_font(20), colors.TEXT, (self.seed_rect.x + 12, self.seed_rect.y + 9))

        mode_label = "カスタム" if self.custom_enabled else "標準 / Seeded"
        draw_text(surface, f"Mode: {mode_label}", get_font(20, bold=True), colors.GOLD, (770, 240))

        draw_text(surface, "Run Modifiers", get_font(28, bold=True), colors.TEXT, (190, 305))
        draw_text(surface, "Modifierを選ぶとカスタムランになり、通常プロフィール集計対象外になります。", get_font(16), colors.MUTED, (190, 340))
        self.modifier_rects.clear()
        y = 378
        mouse = pygame.mouse.get_pos()
        profile = self.app.profile_system.profile
        for modifier_id, item in self.app.registry.run_modifiers.items():
            data = item.data
            unlocked = self.app.unlock_system.is_unlocked(profile, "run_modifier", modifier_id)
            hidden = self.app.unlock_system.is_hidden_until_unlocked("run_modifier", modifier_id)
            rect = pygame.Rect(190, y, 900, 58)
            self.modifier_rects[modifier_id] = rect
            selected = modifier_id in self.selected_modifiers and unlocked
            hovered = rect.collidepoint(mouse)
            pygame.draw.rect(surface, colors.PANEL_LIGHT if hovered or selected else colors.PANEL, rect, border_radius=10)
            pygame.draw.rect(surface, colors.GOLD if selected else (95, 100, 125), rect, width=2, border_radius=10)
            checkbox = "[x]" if selected else "[ ]"
            name = data.get("name", modifier_id) if unlocked or not hidden else "???"
            desc = data.get("description", "") if unlocked else "未解放"
            text_color = colors.GOLD if selected else (colors.TEXT if unlocked else colors.MUTED)
            draw_text(surface, f"{checkbox} {name}", get_font(20, bold=True), text_color, (rect.x + 14, rect.y + 8))
            draw_text(surface, desc, get_font(15), colors.MUTED, (rect.x + 270, rect.y + 12))
            draw_text(surface, data.get("type", "utility"), get_font(14), colors.PURPLE if unlocked else colors.MUTED, (rect.right - 100, rect.y + 34))
            y += 68

        for button in self.buttons:
            button.draw(surface)
        if self.error_message:
            draw_wrapped(surface, self.error_message, get_font(18), colors.RED if "対象外" in self.error_message or "未解放" in self.error_message else colors.TEXT, pygame.Rect(330, 575, 620, 40))
