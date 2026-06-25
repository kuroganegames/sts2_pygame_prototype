from __future__ import annotations

from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class RunResultScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload.get("run_state") or app.run_state
        self.result = payload.get("result", "defeat")
        app.save_system.delete_save()
        self.buttons = [
            Button((500, 500, 280, 58), "タイトルへ", lambda: app.scene_manager.change("title")),
            Button((500, 575, 280, 58), "終了", app.quit),
        ]

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        title = "塔を制覇した" if self.result == "victory" else "倒れてしまった"
        draw_text(surface, title, get_font(52, bold=True), colors.GOLD if self.result == "victory" else colors.RED, (640, 140), center=True)
        if self.run_state:
            p = self.run_state.player
            lines = [
                f"Floor: {self.run_state.floor}",
                f"HP: {p.hp}/{p.max_hp}",
                f"Gold: {p.gold}",
                f"Deck: {len(p.deck)} cards",
                f"Relics: {len(p.relics)}",
                f"Seed: {self.run_state.seed}",
            ]
            y = 240
            for line in lines:
                draw_text(surface, line, get_font(24), colors.TEXT, (640, y), center=True)
                y += 38
        for button in self.buttons:
            button.draw(surface)
