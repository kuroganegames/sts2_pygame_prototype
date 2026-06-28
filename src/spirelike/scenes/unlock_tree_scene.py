from __future__ import annotations

import pygame

from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.unlock_tree_system import UnlockTreeSystem
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text, draw_wrapped


class UnlockTreeScene(BaseScene):
    CATEGORIES = [
        ("all", "All"),
        ("card", "Cards"),
        ("relic", "Relics"),
        ("potion", "Potions"),
        ("run_modifier", "Modifiers"),
        ("character", "Characters"),
    ]

    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.profile = app.profile_system.profile
        self.category = payload.get("category", "all")
        self.tree_system = UnlockTreeSystem(app.registry)
        self.buttons = [Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("profile"))]
        x = 160
        for key, label in self.CATEGORIES:
            self.buttons.append(Button((x, 105, 150, 38), label, lambda k=key: self.set_category(k)))
            x += 160

    def set_category(self, category: str) -> None:
        self.category = category

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "解放ツリー", get_font(44, bold=True), colors.GOLD, (640, 58), center=True)
        draw_text(surface, "解放条件と進捗を確認できます。", get_font(18), colors.MUTED, (640, 92), center=True)
        for button in self.buttons:
            button.draw(surface)

        nodes = self.tree_system.nodes(self.profile, self.category)
        if not nodes:
            draw_text(surface, "表示するUnlockがありません。", get_font(24), colors.MUTED, (640, 320), center=True)
            return

        start_x = 110
        y0 = 165
        node_w = 500
        node_h = 98
        gap_x = 60
        gap_y = 18
        for index, node in enumerate(nodes[:10]):
            col = index % 2
            row = index // 2
            rect = pygame.Rect(start_x + col * (node_w + gap_x), y0 + row * (node_h + gap_y), node_w, node_h)
            self.draw_node(surface, node, rect)
        if len(nodes) > 10:
            draw_text(surface, f"...ほか{len(nodes) - 10}件", get_font(18), colors.MUTED, (640, 690), center=True)

    def draw_node(self, surface, node, rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, colors.PANEL, rect, border_radius=10)
        border = colors.GOLD if node.unlocked else colors.PANEL_LIGHT
        pygame.draw.rect(surface, border, rect, width=2, border_radius=10)
        status = "解除済" if node.unlocked else "未解放"
        title_color = colors.GOLD if node.unlocked else colors.MUTED
        draw_text(surface, f"[{status}] {node.name}", get_font(19, bold=True), title_color, (rect.x + 14, rect.y + 8))
        draw_text(surface, f"Tier {node.tier} / {node.target_type}: {node.target_id}", get_font(13), colors.PURPLE, (rect.right - 210, rect.y + 12))
        if node.description:
            draw_wrapped(surface, node.description, get_font(14), colors.TEXT, pygame.Rect(rect.x + 14, rect.y + 34, rect.width - 28, 22))
        y = rect.y + 60
        if node.hidden:
            draw_text(surface, "条件: 隠された条件", get_font(14), colors.MUTED, (rect.x + 14, y))
            return
        lines = node.condition_lines or ["条件なし"]
        for line in lines[:2]:
            draw_text(surface, line, get_font(14), colors.TEXT, (rect.x + 14, y))
            y += 18
        if len(lines) > 2:
            draw_text(surface, f"...ほか{len(lines) - 2}条件", get_font(13), colors.MUTED, (rect.x + 14, y))
