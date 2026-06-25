from __future__ import annotations

from spirelike.models.selection import CardSelectionRequest
from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class RestScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload["run_state"]
        self.node_id = payload["node_id"]
        self.buttons = [
            Button((430, 250, 200, 70), "休憩: 30%回復", self.rest),
            Button((650, 250, 200, 70), "鍛冶: 1枚強化", self.upgrade),
            Button((540, 600, 200, 52), "戻る", self.finish),
        ]

    def rest(self) -> None:
        amount = int(self.run_state.player.max_hp * 0.30)
        healed = self.run_state.player.heal(amount)
        self.run_state.add_message(f"休憩: HPを{healed}回復")
        self.finish()

    def upgrade(self) -> None:
        request = CardSelectionRequest(
            title="鍛冶",
            message="強化するカードを1枚選んでください。",
            source_zones=["master_deck"],
            exact_count=1,
            min_count=1,
            max_count=1,
            filter={"can_upgrade": True},
            operation={"type": "upgrade"},
        )
        self.app.scene_manager.change(
            "card_select",
            {
                "run_state": self.run_state,
                "request": request,
                "return_scene": "map",
                "return_payload": {"run_state": self.run_state},
                "finish_node_id": self.node_id,
            },
        )

    def finish(self) -> None:
        self.run_state.map_state.mark_visited(self.node_id)
        self.app.scene_manager.change("map", {"run_state": self.run_state})

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "休憩所", get_font(42, bold=True), colors.GOLD, (640, 70), center=True)
        p = self.run_state.player
        draw_text(surface, f"HP {p.hp}/{p.max_hp}", get_font(24), colors.TEXT, (640, 130), center=True)
        for button in self.buttons:
            button.draw(surface)
