from __future__ import annotations

from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class RunHistoryScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.profile = app.profile_system.profile
        self.buttons = [Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("profile"))]

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "ラン履歴", get_font(44, bold=True), colors.GOLD, (640, 70), center=True)
        history = self.profile.run_history[:12]
        if not history:
            draw_text(surface, "まだラン履歴がありません。", get_font(24), colors.MUTED, (640, 260), center=True)
        y = 130
        for index, record in enumerate(history, start=1):
            character_id = record.get("character_id", "?")
            char_name = self.app.registry.characters.get(character_id).data.get("name", character_id) if character_id in self.app.registry.characters else character_id
            result = record.get("result", "?")
            floor = record.get("floor", 0)
            seed = record.get("seed", "?")
            deck_size = record.get("deck_size", 0)
            mode = record.get("mode", "standard")
            eligibility = "" if record.get("profile_eligible", True) else " [Custom]"
            mods = record.get("selected_modifiers", []) or []
            mod_text = f" Mods:{','.join(mods[:2])}" if mods else ""
            text = f"#{index} {char_name} / {mode}{eligibility} / {result} / Floor {floor} / Deck {deck_size} / Seed {seed}{mod_text}"
            draw_text(surface, text, get_font(18), colors.TEXT, (110, y))
            y += 38
        for button in self.buttons:
            button.draw(surface)
