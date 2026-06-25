from __future__ import annotations

import pygame

from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class CompendiumScene(BaseScene):
    CATEGORIES = [
        ("cards", "カード"),
        ("relics", "レリック"),
        ("potions", "ポーション"),
        ("card_modifiers", "Modifier"),
        ("ancients", "Ancient"),
    ]

    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.profile = app.profile_system.profile
        self.category = payload.get("category", "cards")
        self.buttons = [Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("profile"))]
        x = 180
        for key, label in self.CATEGORIES:
            self.buttons.append(Button((x, 100, 150, 40), label, lambda k=key: self.set_category(k)))
            x += 165

    def set_category(self, category: str) -> None:
        self.category = category

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "コレクション", get_font(44, bold=True), colors.GOLD, (640, 58), center=True)
        for button in self.buttons:
            button.draw(surface)
        category_label = dict(self.CATEGORIES).get(self.category, self.category)
        draw_text(surface, category_label, get_font(28, bold=True), colors.TEXT, (640, 158), center=True)
        items = self._registry_items()
        discovered = self.profile.compendium.get(self.category, {})
        x, y = 110, 205
        for index, item_id in enumerate(items):
            entry = discovered.get(item_id, {})
            seen = bool(entry.get("seen"))
            rect = pygame.Rect(x + (index % 2) * 540, y + (index // 2) * 62, 500, 48)
            pygame.draw.rect(surface, colors.PANEL, rect, border_radius=8)
            name = self._display_name(item_id) if seen else "???"
            draw_text(surface, name, get_font(18, bold=True), colors.GOLD if seen else colors.MUTED, (rect.x + 14, rect.y + 8))
            detail = self._entry_detail(entry) if seen else "未発見"
            draw_text(surface, detail, get_font(14), colors.TEXT, (rect.x + 220, rect.y + 12))

    def _registry_items(self) -> list[str]:
        if self.category == "cards":
            return list(self.app.registry.cards.keys())
        if self.category == "relics":
            return list(self.app.registry.relics.keys())
        if self.category == "potions":
            return list(self.app.registry.potions.keys())
        if self.category == "card_modifiers":
            return list(self.app.registry.card_modifiers.keys())
        if self.category == "ancients":
            return list(self.app.registry.ancients.keys())
        return []

    def _display_name(self, item_id: str) -> str:
        if self.category == "cards":
            return self.app.registry.card(item_id).get("name", item_id)
        if self.category == "relics":
            return self.app.registry.relic(item_id).get("name", item_id)
        if self.category == "potions":
            return self.app.registry.potion(item_id).get("name", item_id)
        if self.category == "card_modifiers":
            return self.app.registry.card_modifier(item_id).get("name", item_id)
        if self.category == "ancients":
            return self.app.registry.ancient(item_id).get("name", item_id)
        return item_id

    def _entry_detail(self, entry: dict) -> str:
        if self.category == "cards":
            return f"獲得 {entry.get('acquired', 0)} / 使用 {entry.get('played', 0)} / 強化 {entry.get('upgraded', 0)}"
        if self.category == "relics":
            return f"獲得 {entry.get('acquired', 0)}"
        if self.category == "potions":
            return f"獲得 {entry.get('acquired', 0)} / 使用 {entry.get('used', 0)}"
        if self.category == "card_modifiers":
            return f"付与 {entry.get('applied', 0)} / 浄化 {entry.get('cleansed', 0)}"
        if self.category == "ancients":
            choices = entry.get("choices", {}) or {}
            return f"選択 {sum(choices.values())}"
        return ""
