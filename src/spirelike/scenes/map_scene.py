from __future__ import annotations

import pygame

from spirelike.core.rng import RunRng
from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.map_generator import MapGenerator
from spirelike.systems.reward_system import RewardSystem
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text


NODE_COLORS = {
    "monster": (170, 85, 85),
    "elite": (205, 120, 60),
    "event": (110, 100, 180),
    "shop": (210, 185, 80),
    "rest": (90, 175, 120),
    "treasure": (185, 150, 70),
    "ancient": (90, 150, 205),
    "boss": (220, 70, 70),
}

NODE_LABELS = {
    "monster": "M",
    "elite": "E",
    "event": "?",
    "shop": "$",
    "rest": "R",
    "treasure": "T",
    "ancient": "A",
    "boss": "B",
}


class MapScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload.get("run_state") or app.run_state
        self.app.run_state = self.run_state
        self.node_rects: dict[str, pygame.Rect] = {}
        self.buttons = [Button((1120, 24, 130, 42), "タイトル", lambda: app.scene_manager.change("title"))]

    def handle_event(self, event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for node_id, rect in self.node_rects.items():
                node = self.run_state.map_state.nodes[node_id]
                if rect.collidepoint(event.pos) and node.available and not node.visited:
                    self.enter_node(node_id)
                    return

    def enter_node(self, node_id: str) -> None:
        node = self.run_state.map_state.nodes[node_id]
        self.run_state.floor += 1
        rngs = RunRng(self.run_state.seed + self.run_state.floor)
        if node.node_type in {"monster", "elite", "boss"}:
            enemy_ids = MapGenerator(self.app.registry).choose_encounter(
                self.run_state.map_state.act_id, node.node_type, rngs.combat
            )
            self.app.scene_manager.change(
                "combat",
                {
                    "run_state": self.run_state,
                    "node_id": node_id,
                    "node_type": node.node_type,
                    "enemy_ids": enemy_ids,
                },
            )
        elif node.node_type == "treasure":
            reward = RewardSystem(self.app.registry).treasure_reward(self.run_state, rngs.reward)
            self.app.scene_manager.change(
                "reward", {"run_state": self.run_state, "node_id": node_id, "reward": reward}
            )
        elif node.node_type == "rest":
            self.app.scene_manager.change("rest", {"run_state": self.run_state, "node_id": node_id})
        elif node.node_type == "shop":
            self.app.scene_manager.change("shop", {"run_state": self.run_state, "node_id": node_id})
        elif node.node_type == "event":
            self.app.scene_manager.change("event", {"run_state": self.run_state, "node_id": node_id})
        elif node.node_type == "ancient":
            self.app.scene_manager.change(
                "ancient",
                {"run_state": self.run_state, "node_id": node_id, "after": "map", "phase": "node"},
            )
        else:
            self.run_state.map_state.mark_visited(node_id)

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        run = self.run_state
        player = run.player
        draw_text(surface, "マップ", get_font(38, bold=True), colors.TEXT, (40, 28))
        draw_text(surface, f"HP {player.hp}/{player.max_hp}   Gold {player.gold}   Deck {len(player.deck)}", get_font(22), colors.GOLD, (40, 78))
        potion_text = " / ".join(
            self.app.registry.potion(p.potion_id).get("name", p.potion_id) if p else "空"
            for p in player.potions
        )
        draw_text(surface, f"Potions: {potion_text}", get_font(16), colors.MUTED, (40, 108))
        draw_text(surface, f"Seed {run.seed} / Floor {run.floor}", get_font(16), colors.MUTED, (40, 130))

        map_rect = pygame.Rect(70, 160, 900, 510)
        self.node_rects.clear()
        nodes = run.map_state.nodes
        for node in nodes.values():
            for next_id in node.connected_to:
                if next_id not in nodes:
                    continue
                p1 = self._node_pos(map_rect, node)
                p2 = self._node_pos(map_rect, nodes[next_id])
                pygame.draw.line(surface, (90, 95, 110), p1, p2, width=2)

        for node in nodes.values():
            pos = self._node_pos(map_rect, node)
            radius = 20 if node.node_type != "boss" else 26
            rect = pygame.Rect(pos[0] - radius, pos[1] - radius, radius * 2, radius * 2)
            self.node_rects[node.id] = rect
            color = NODE_COLORS.get(node.node_type, colors.PANEL_LIGHT)
            if node.visited:
                color = (70, 75, 85)
            elif not node.available:
                color = tuple(max(20, c - 70) for c in color)
            pygame.draw.circle(surface, color, pos, radius)
            border = colors.GOLD if node.available and not node.visited else colors.WHITE
            pygame.draw.circle(surface, border, pos, radius, width=2)
            draw_text(surface, NODE_LABELS.get(node.node_type, "?"), get_font(20, bold=True), colors.WHITE, pos, center=True)

        panel = pygame.Rect(1010, 140, 230, 410)
        pygame.draw.rect(surface, colors.PANEL, panel, border_radius=12)
        pygame.draw.rect(surface, colors.PANEL_LIGHT, panel, width=2, border_radius=12)
        draw_text(surface, "ログ", get_font(24, bold=True), colors.TEXT, (panel.x + 18, panel.y + 16))
        y = panel.y + 58
        for msg in reversed(run.messages):
            draw_text(surface, msg, get_font(16), colors.MUTED, (panel.x + 18, y))
            y += 28

        for button in self.buttons:
            button.draw(surface)

    def _node_pos(self, rect: pygame.Rect, node) -> tuple[int, int]:
        x = rect.x + int(node.x * rect.width)
        y = rect.y + int(node.y * rect.height)
        return x, y
