from __future__ import annotations

import pygame

from spirelike.core.rng import RunRng
from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.card_operation_system import CardOperationSystem
from spirelike.systems.card_selection_system import CardSelectionSystem
from spirelike.systems.run_effects import RunEffectExecutor
from spirelike.ui import colors
from spirelike.ui.card_selection_view import CardSelectionView
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


class CardSelectScene(BaseScene):
    """戦闘外の汎用カード選択Scene。休憩所、イベント、エンシェントから使う。"""

    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload["run_state"]
        self.request = payload.get("request") or self.run_state.pending_selection
        self.return_scene = payload.get("return_scene", "map")
        self.return_payload = payload.get("return_payload", {"run_state": self.run_state})
        self.finish_node_id = payload.get("finish_node_id")
        self.rng = RunRng(self.run_state.seed + self.run_state.floor + 4919).event
        self.selection_system = CardSelectionSystem(app.registry)
        self.operation_system = CardOperationSystem(app.registry, self.rng)
        self.executor = RunEffectExecutor(app.registry, self.rng)
        self.view: CardSelectionView | None = None
        self._build_view()

    def _build_view(self) -> None:
        if self.request is None:
            self.view = None
            return
        candidates = self.selection_system.collect_candidates(self.run_state, self.request, None)
        self.view = CardSelectionView(self.app.registry, self.request, candidates)

    def handle_event(self, event) -> None:
        if self.view is None:
            return
        result = self.view.handle_event(event)
        if result is None:
            return

        request = self.request
        if request is None:
            self.finish()
            return

        self.operation_system.apply_result(self.run_state, request, result, combat=None)
        self.run_state.pending_selection = None
        remaining = list(self.run_state.pending_effects)
        self.run_state.pending_effects = []

        if remaining:
            self.executor.execute_many(self.run_state, remaining)

        if self.run_state.pending_selection is not None:
            self.request = self.run_state.pending_selection
            self._build_view()
            return

        self.finish()

    def finish(self) -> None:
        if self.finish_node_id:
            self.run_state.map_state.mark_visited(self.finish_node_id)
        payload = dict(self.return_payload or {})
        payload.setdefault("run_state", self.run_state)
        self.app.scene_manager.change(self.return_scene, payload)

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        draw_text(surface, "カード選択", get_font(40, bold=True), colors.GOLD, (640, 56), center=True)
        if self.view:
            self.view.draw(surface)
        else:
            draw_text(surface, "選択リクエストがありません。", get_font(24), colors.TEXT, (640, 300), center=True)
