from __future__ import annotations

from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class ProfileScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.profile = app.profile_system.profile
        self.buttons = [
            Button((500, 400, 280, 48), "ラン履歴", lambda: app.scene_manager.change("run_history")),
            Button((500, 460, 280, 48), "敵図鑑", lambda: app.scene_manager.change("bestiary")),
            Button((500, 520, 280, 48), "コレクション", lambda: app.scene_manager.change("compendium")),
            Button((500, 580, 280, 48), "Timeline", lambda: app.scene_manager.change("timeline")),
            Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("title")),
        ]

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        summary = self.profile.summary
        compendium = self.profile.compendium
        draw_text(surface, "プロフィール", get_font(44, bold=True), colors.GOLD, (640, 70), center=True)
        lines = [
            f"総ラン数: {summary.get('runs_started', 0)}",
            f"完了ラン: {summary.get('runs_completed', 0)}",
            f"勝利: {summary.get('victories', 0)} / 敗北: {summary.get('defeats', 0)}",
            f"最高到達階: {summary.get('highest_floor', 0)} / Act {summary.get('highest_act', 0)}",
            f"倒した敵: {summary.get('total_enemies_defeated', 0)}",
            f"見つけたカード: {len(compendium.get('cards', {}))} / {len(self.app.registry.cards)}",
            f"見つけたレリック: {len(compendium.get('relics', {}))} / {len(self.app.registry.relics)}",
            f"Timeline: {len(self.profile.timeline.get('unlocked_fragments', []))} / {len(self.app.registry.timeline_fragments)}",
        ]
        y = 135
        for line in lines:
            draw_text(surface, line, get_font(24), colors.TEXT, (440, y))
            y += 32
        for button in self.buttons:
            button.draw(surface)
