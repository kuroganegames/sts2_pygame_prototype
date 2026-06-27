from __future__ import annotations

import pygame

from spirelike.save.save_slot import SaveSlotSummary
from spirelike.scenes.base_scene import BaseScene
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text, draw_wrapped


class SaveSlotScene(BaseScene):
    def __init__(self, app, payload: dict) -> None:
        super().__init__(app, payload)
        self.mode = payload.get("mode", "load")
        self.slots = app.save_system.list_slots()
        self.slot_rects: dict[str, pygame.Rect] = {}
        self.selected_slot_id: str | None = None
        self.confirm_overwrite_slot_id: str | None = None
        self.confirm_delete_slot_id: str | None = None
        self.message = ""
        action_label = "このスロットで開始" if self.mode == "new" else "このスロットを開く"
        self.action_button = Button((420, 620, 210, 50), action_label, self.perform_action)
        self.delete_button = Button((650, 620, 150, 50), "削除", self.delete_selected)
        self.buttons = [
            Button((30, 30, 130, 44), "戻る", lambda: app.scene_manager.change("title")),
            self.action_button,
            self.delete_button,
        ]

    def refresh_slots(self) -> None:
        self.slots = self.app.save_system.list_slots()
        if self.selected_slot_id and not any(slot.slot_id == self.selected_slot_id for slot in self.slots):
            self.selected_slot_id = None

    def handle_event(self, event) -> None:
        super().handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for slot in self.slots:
                rect = self.slot_rects.get(slot.slot_id)
                if rect and rect.collidepoint(event.pos):
                    self.selected_slot_id = slot.slot_id
                    self.confirm_delete_slot_id = None
                    if self.mode == "new" and slot.exists and self.confirm_overwrite_slot_id != slot.slot_id:
                        self.confirm_overwrite_slot_id = slot.slot_id
                        self.message = "このスロットは上書きされます。もう一度『このスロットで開始』を押してください。"
                    else:
                        self.message = ""
                    return

    def selected_slot(self) -> SaveSlotSummary | None:
        for slot in self.slots:
            if slot.slot_id == self.selected_slot_id:
                return slot
        return None

    def perform_action(self) -> None:
        slot = self.selected_slot()
        if slot is None:
            self.message = "スロットを選択してください。"
            return
        if self.mode == "load":
            if not slot.exists or slot.is_corrupt:
                self.message = "このスロットは開けません。"
                return
            if not self.app.continue_saved_run(slot.slot_id):
                self.message = self.app.last_load_error or "ロードに失敗しました。"
            return

        # new mode
        if slot.exists and self.confirm_overwrite_slot_id != slot.slot_id:
            self.confirm_overwrite_slot_id = slot.slot_id
            self.message = "既存ランを上書きします。もう一度押すと続行します。"
            return
        self.app.scene_manager.change("character_select", {"save_slot_id": slot.slot_id})

    def delete_selected(self) -> None:
        slot = self.selected_slot()
        if slot is None or not slot.exists:
            self.message = "削除するスロットを選択してください。"
            return
        if self.confirm_delete_slot_id != slot.slot_id:
            self.confirm_delete_slot_id = slot.slot_id
            self.message = "もう一度『削除』を押すと、このスロットを削除します。"
            return
        self.app.save_system.delete_slot(slot.slot_id)
        self.message = f"{slot.display_name} を削除しました。"
        self.selected_slot_id = None
        self.confirm_delete_slot_id = None
        self.confirm_overwrite_slot_id = None
        self.refresh_slots()

    def draw(self, surface) -> None:
        surface.fill(colors.BG)
        title = "新規ラン: 保存先を選択" if self.mode == "new" else "続きから: セーブを選択"
        draw_text(surface, title, get_font(42, bold=True), colors.GOLD, (640, 60), center=True)
        draw_text(surface, "複数の進行中ランを保存できます。", get_font(20), colors.MUTED, (640, 104), center=True)

        self.slot_rects.clear()
        start_x = 155
        y = 155
        slot_w = 300
        gap = 35
        for i, slot in enumerate(self.slots):
            rect = pygame.Rect(start_x + i * (slot_w + gap), y, slot_w, 360)
            self.slot_rects[slot.slot_id] = rect
            selected = slot.slot_id == self.selected_slot_id
            hovered = rect.collidepoint(pygame.mouse.get_pos())
            fill = colors.PANEL_LIGHT if hovered or selected else colors.PANEL
            border = colors.GOLD if selected else (110, 115, 140)
            pygame.draw.rect(surface, fill, rect, border_radius=14)
            pygame.draw.rect(surface, border, rect, width=3 if selected else 2, border_radius=14)
            self.draw_slot(surface, slot, rect)

        slot = self.selected_slot()
        self.action_button.enabled = slot is not None and (self.mode == "new" or (slot.exists and not slot.is_corrupt))
        self.delete_button.enabled = slot is not None and slot.exists
        for button in self.buttons:
            button.draw(surface)
        if self.message:
            draw_wrapped(surface, self.message, get_font(18), colors.RED if "削除" in self.message or "上書き" in self.message else colors.TEXT, pygame.Rect(320, 548, 640, 52))

    def draw_slot(self, surface, slot: SaveSlotSummary, rect: pygame.Rect) -> None:
        draw_text(surface, slot.display_name or f"Slot {slot.slot_index}", get_font(26, bold=True), colors.GOLD, (rect.x + 18, rect.y + 18))
        if not slot.exists:
            draw_text(surface, "空き", get_font(28, bold=True), colors.MUTED, (rect.centerx, rect.centery), center=True)
            return
        if slot.is_corrupt:
            draw_text(surface, "破損したセーブ", get_font(22, bold=True), colors.RED, (rect.x + 18, rect.y + 70))
            draw_wrapped(surface, slot.error, get_font(15), colors.TEXT, pygame.Rect(rect.x + 18, rect.y + 108, rect.width - 36, 160))
            return
        lines = [
            f"{slot.character_name}",
            f"{slot.scene_label} / Floor {slot.floor}",
            f"Act {slot.act} / Seed {slot.seed}",
            f"HP {slot.hp}/{slot.max_hp}",
            f"Gold {slot.gold}",
            f"Deck {slot.deck_size} / Relics {slot.relic_count}",
            f"Saved:",
            slot.saved_at[:19].replace("T", " "),
        ]
        y = rect.y + 72
        for index, line in enumerate(lines):
            color = colors.TEXT if index != 0 else colors.GOLD
            font = get_font(20, bold=(index == 0)) if index < 6 else get_font(14)
            draw_text(surface, line, font, color, (rect.x + 18, y))
            y += 34 if index < 6 else 22
