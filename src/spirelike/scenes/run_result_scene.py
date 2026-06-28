from __future__ import annotations

from spirelike.profile.progression_result import ProgressionResult
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
        self.progression = ProgressionResult()
        if self.run_state:
            self.progression = app.profile_system.finalize_run(self.run_state, self.result)
            app.save_system.delete_slot(self.run_state.flags.get("save_slot_id"))
        else:
            app.save_system.delete_save()
        self.buttons = [
            Button((500, 610, 280, 50), "タイトルへ", lambda: app.scene_manager.change("title")),
            Button((500, 665, 280, 50), "終了", app.quit),
        ]

    def progression_lines(self) -> list[str]:
        lines: list[str] = []
        for item in self.progression.new_difficulty_unlocks:
            lines.append(str(item.get("title", "Difficulty解放")))
        for item in self.progression.new_timeline_fragments:
            lines.append(f"Timeline: {item.get('title')}")
        for rule in self.progression.new_content_unlocks:
            lines.append(f"解放: {rule.get('name', rule.get('target_id'))}")
        for achievement in self.progression.new_achievements:
            lines.append(f"実績解除: {achievement.get('name', achievement.get('id'))}")
        return lines

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        title = "塔を制覇した" if self.result == "victory" else "倒れてしまった"
        draw_text(surface, title, get_font(50, bold=True), colors.GOLD if self.result == "victory" else colors.RED, (640, 72), center=True)
        if self.run_state:
            p = self.run_state.player
            lines = [
                f"Floor: {self.run_state.floor}",
                f"HP: {p.hp}/{p.max_hp}",
                f"Gold: {p.gold}",
                f"Deck: {len(p.deck)} cards",
                f"Relics: {len(p.relics)}",
                f"Seed: {self.run_state.seed}",
                f"Slot: {self.run_state.flags.get('save_slot_id', '-')}",
            ]
            y = 140
            for line in lines:
                draw_text(surface, line, get_font(22), colors.TEXT, (360, y), center=True)
                y += 32

        progression_lines = self.progression_lines()
        if progression_lines:
            draw_text(surface, "新規解放", get_font(28, bold=True), colors.GOLD, (820, 140), center=True)
            y = 185
            max_lines = 8
            for line in progression_lines[:max_lines]:
                draw_text(surface, line, get_font(19), colors.TEXT, (690, y))
                y += 30
            remaining = len(progression_lines) - max_lines
            if remaining > 0:
                draw_text(surface, f"...ほか{remaining}件", get_font(18), colors.MUTED, (690, y))
        else:
            draw_text(surface, "新規解放はありません。", get_font(20), colors.MUTED, (820, 190), center=True)

        for button in self.buttons:
            button.draw(surface)
