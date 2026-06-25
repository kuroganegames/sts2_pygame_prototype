from __future__ import annotations

import pygame

from spirelike.core.rng import RunRng
from spirelike.models.entities import EnemyInstance
from spirelike.scenes.base_scene import BaseScene
from spirelike.systems.card_selection_system import CardSelectionSystem
from spirelike.systems.combat_system import CombatSystem
from spirelike.systems.potion_system import PotionSystem
from spirelike.systems.reward_system import RewardSystem
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.card_selection_view import CardSelectionView
from spirelike.ui.card_view import CardView
from spirelike.ui.fonts import get_font
from spirelike.ui.images import image_cache
from spirelike.ui.potion_bar import PotionBar
from spirelike.ui.text import draw_text


class CombatScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.run_state = payload["run_state"]
        self.node_id = payload["node_id"]
        self.node_type = payload.get("node_type", "monster")
        self.enemy_ids = payload.get("enemy_ids", [])
        rngs = RunRng(self.run_state.seed + self.run_state.floor)
        self.combat = CombatSystem(app.registry, self.run_state, self.enemy_ids, rngs.combat)
        self.potion_system = PotionSystem(app.registry)
        self.selection_system = CardSelectionSystem(app.registry)
        self.selection_view: CardSelectionView | None = None
        self.selection_request_id: str | None = None
        self.selected_card = None
        self.selected_potion_slot: int | None = None
        self.card_rects: dict[str, pygame.Rect] = {}
        self.enemy_rects: dict[str, pygame.Rect] = {}
        self.potion_rects: dict[int, pygame.Rect] = {}
        self.buttons = [Button((1110, 610, 140, 52), "ターン終了", self.end_turn)]

    def end_turn(self) -> None:
        self.selected_card = None
        self.selected_potion_slot = None
        self.combat.end_player_turn()
        self._after_state_change()

    def handle_event(self, event) -> None:
        if self.combat.state.pending_selection is not None:
            self._ensure_selection_view()
            if self.selection_view:
                result = self.selection_view.handle_event(event)
                if result:
                    self.selection_view = None
                    self.selection_request_id = None
                    self.combat.complete_card_selection(result)
                    self._after_state_change()
            return

        super().handle_event(event)
        if event.type == pygame.MOUSEMOTION:
            pass
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            # ポーション対象選択中に敵をクリック
            if self.selected_potion_slot is not None:
                for enemy in self.combat.state.alive_enemies():
                    rect = self.enemy_rects.get(enemy.enemy_id + str(id(enemy)))
                    if rect and rect.collidepoint(pos):
                        self.potion_system.use_in_combat(self.combat, self.selected_potion_slot, enemy)
                        self.selected_potion_slot = None
                        self._after_state_change()
                        return

            # カード対象選択中に敵をクリック
            if self.selected_card is not None:
                for enemy in self.combat.state.alive_enemies():
                    rect = self.enemy_rects.get(enemy.enemy_id + str(id(enemy)))
                    if rect and rect.collidepoint(pos):
                        self.combat.play_card(self.selected_card, enemy)
                        self.selected_card = None
                        self._after_state_change()
                        return

            # ポーションクリック
            for slot_index, rect in self.potion_rects.items():
                if rect.collidepoint(pos):
                    self.on_potion_clicked(slot_index)
                    return

            # カードクリック
            for card in list(self.combat.state.hand):
                rect = self.card_rects.get(card.instance_id)
                if rect and rect.collidepoint(pos):
                    self.on_card_clicked(card)
                    return

    def _ensure_selection_view(self) -> None:
        request = self.combat.state.pending_selection
        if request is None:
            self.selection_view = None
            self.selection_request_id = None
            return
        if self.selection_view is not None and self.selection_request_id == request.request_id:
            return
        candidates = self.selection_system.collect_candidates(self.run_state, request, self.combat.state)
        self.selection_view = CardSelectionView(self.app.registry, request, candidates)
        self.selection_request_id = request.request_id

    def on_potion_clicked(self, slot_index: int) -> None:
        potion = self.run_state.player.potions[slot_index]
        if potion is None:
            return
        potion_def = self.app.registry.potion(potion.potion_id)
        ok, reason = self.potion_system.can_use_in_combat(self.run_state, slot_index)
        if not ok:
            self.combat.log(reason)
            return
        self.selected_card = None
        if potion_def.get("target") == "enemy":
            self.selected_potion_slot = slot_index
            self.combat.log("ポーション対象の敵を選択")
        else:
            self.potion_system.use_in_combat(self.combat, slot_index, None)
            self.selected_potion_slot = None
            self._after_state_change()

    def on_card_clicked(self, card) -> None:
        card_def = self.app.registry.card(card.card_id)
        ok, reason = self.combat.can_play(card)
        if not ok:
            self.combat.log(reason)
            return
        self.selected_potion_slot = None
        if card_def.get("target") == "enemy":
            self.selected_card = card
            self.combat.log("敵を選択")
        else:
            self.combat.play_card(card, None)
            self._after_state_change()

    def _after_state_change(self) -> None:
        outcome = self.combat.state.outcome
        if outcome == "victory":
            if self.node_type == "boss":
                reward = RewardSystem(self.app.registry).combat_reward(self.run_state, self.node_type, RunRng(self.run_state.seed + self.run_state.floor).reward)
                self.app.scene_manager.change(
                    "reward",
                    {
                        "run_state": self.run_state,
                        "node_id": self.node_id,
                        "reward": reward,
                        "after_boss": True,
                    },
                )
            else:
                reward = RewardSystem(self.app.registry).combat_reward(self.run_state, self.node_type, RunRng(self.run_state.seed + self.run_state.floor).reward)
                self.app.scene_manager.change(
                    "reward", {"run_state": self.run_state, "node_id": self.node_id, "reward": reward}
                )
        elif outcome == "defeat":
            self.app.scene_manager.change("run_result", {"run_state": self.run_state, "result": "defeat"})

    def draw(self, surface) -> None:
        surface.fill((28, 24, 28))
        state = self.combat.state
        player = self.run_state.player
        draw_text(surface, "戦闘", get_font(32, bold=True), colors.TEXT, (40, 20))
        draw_text(surface, f"HP {player.hp}/{player.max_hp}   Block {player.block}   Energy {state.energy}/{player.base_energy}   Gold {player.gold}", get_font(22), colors.GOLD, (40, 62))
        draw_text(surface, f"Draw {len(state.draw_pile)} / Discard {len(state.discard_pile)} / Exhaust {len(state.exhaust_pile)}", get_font(18), colors.MUTED, (40, 94))

        self.potion_rects = PotionBar(self.app.registry, self.run_state, (400, 38)).draw(surface)

        if self.selected_potion_slot is not None:
            draw_text(surface, "ポーション対象を選択中", get_font(18, bold=True), colors.GOLD, (690, 64))
        elif self.selected_card is not None:
            draw_text(surface, "カード対象を選択中", get_font(18, bold=True), colors.GOLD, (690, 64))
        elif state.pending_selection is not None:
            draw_text(surface, "カード選択中", get_font(18, bold=True), colors.GOLD, (690, 64))

        if state.powers:
            power_text = " / ".join(f"{p.power_id}x{p.stacks}" for p in state.powers)
            draw_text(surface, f"Powers: {power_text}", get_font(15), colors.PURPLE, (40, 122))

        self.enemy_rects.clear()
        alive = state.alive_enemies()
        total = max(1, len(alive))
        for i, enemy in enumerate(alive):
            x = 720 + i * 180 - (total - 1) * 70
            y = 185
            self.draw_enemy(surface, enemy, (x, y))

        # 手札
        self.card_rects.clear()
        hand = state.hand
        card_w, card_h = self.app.settings.card_width, self.app.settings.card_height
        total_w = len(hand) * (card_w + 8) - 8
        start_x = max(20, (self.app.settings.screen_width - total_w) // 2)
        y = 500
        mouse = pygame.mouse.get_pos()
        for i, card in enumerate(hand):
            rect = pygame.Rect(start_x + i * (card_w + 8), y, card_w, card_h)
            self.card_rects[card.instance_id] = rect
            enabled = self.combat.can_play(card)[0]
            view = CardView(self.app.registry, rect, card, enabled=enabled)
            view.handle_motion(mouse)
            if self.selected_card is card:
                view.hovered = True
            view.draw(surface)

        log_panel = pygame.Rect(30, 145, 360, 235)
        pygame.draw.rect(surface, colors.PANEL, log_panel, border_radius=12)
        draw_text(surface, "ログ", get_font(20, bold=True), colors.TEXT, (log_panel.x + 14, log_panel.y + 10))
        y = log_panel.y + 42
        for line in reversed(state.log[-7:]):
            draw_text(surface, line, get_font(15), colors.MUTED, (log_panel.x + 14, y))
            y += 25

        for button in self.buttons:
            button.draw(surface)

        if self.combat.state.pending_selection is not None:
            self._ensure_selection_view()
            if self.selection_view:
                self.selection_view.draw(surface)

    def draw_enemy(self, surface, enemy: EnemyInstance, pos: tuple[int, int]) -> None:
        x, y = pos
        rect = pygame.Rect(x, y, 140, 180)
        key = enemy.enemy_id + str(id(enemy))
        self.enemy_rects[key] = rect
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surface, colors.PANEL_LIGHT if hovered else colors.PANEL, rect, border_radius=12)
        pygame.draw.rect(surface, colors.GOLD if hovered else colors.WHITE, rect, width=2, border_radius=12)
        image_path = self.app.registry.enemies[enemy.enemy_id].image_path
        art_rect = pygame.Rect(rect.x + 25, rect.y + 16, 90, 75)
        surface.blit(image_cache.load(image_path, art_rect.size), art_rect)
        draw_text(surface, enemy.name, get_font(17, bold=True), colors.TEXT, (rect.centerx, rect.y + 108), center=True)
        draw_text(surface, f"HP {enemy.hp}/{enemy.max_hp}  B {enemy.block}", get_font(16), colors.GOLD, (rect.centerx, rect.y + 132), center=True)
        move_name = self._move_label(enemy)
        draw_text(surface, move_name, get_font(15), colors.RED, (rect.centerx, rect.y + 156), center=True)
        if enemy.statuses:
            status_text = " ".join(f"{k}:{v}" for k, v in enemy.statuses.items())
            draw_text(surface, status_text, get_font(12), colors.MUTED, (rect.x + 8, rect.bottom - 20))

    def _move_label(self, enemy: EnemyInstance) -> str:
        if not enemy.next_move:
            return ""
        move = self.app.registry.enemy(enemy.enemy_id).get("moves", {}).get(enemy.next_move, {})
        intent = move.get("intent", "?")
        amount = ""
        for effect in move.get("effects", []) or []:
            if effect.get("type") == "damage":
                amount = f" {effect.get('amount', '')}"
                break
        return f"{intent}{amount}"
