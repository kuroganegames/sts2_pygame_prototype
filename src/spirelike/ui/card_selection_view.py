from __future__ import annotations

import pygame

from spirelike.content.loader import ContentRegistry
from spirelike.models.selection import CardSelectionCandidate, CardSelectionRequest, CardSelectionResult
from spirelike.ui import colors
from spirelike.ui.buttons import Button
from spirelike.ui.card_view import CardView
from spirelike.ui.fonts import get_font
from spirelike.ui.text import draw_text, draw_wrapped


ZONE_LABELS = {
    "master_deck": "デッキ",
    "hand": "手札",
    "draw_pile": "山札",
    "discard_pile": "捨て札",
    "exhaust_pile": "廃棄札",
    "limbo": "使用中",
}


class CardSelectionView:
    def __init__(
        self,
        registry: ContentRegistry,
        request: CardSelectionRequest,
        candidates: list[CardSelectionCandidate],
        rect: pygame.Rect | None = None,
    ) -> None:
        self.registry = registry
        self.request = request
        self.candidates = candidates
        self.rect = rect or pygame.Rect(110, 70, 1060, 600)
        self.selected_ids: set[str] = set()
        self.page = 0
        self.cards_per_page = 5
        self.card_rects: dict[str, pygame.Rect] = {}
        self.confirm_button = Button((self.rect.right - 190, self.rect.bottom - 58, 150, 44), "決定", lambda: None)
        self.skip_button = Button((self.rect.right - 355, self.rect.bottom - 58, 150, 44), "スキップ", lambda: None)

    def handle_event(self, event) -> CardSelectionResult | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.request.allow_skip:
                return CardSelectionResult(self.request.request_id, [], skipped=True)
            if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.can_confirm():
                return self.result()
            if event.key == pygame.K_RIGHT:
                self.next_page()
            if event.key == pygame.K_LEFT:
                self.prev_page()

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        pos = event.pos
        if self.confirm_button.rect.collidepoint(pos) and self.can_confirm():
            return self.result()
        if self.request.allow_skip and self.skip_button.rect.collidepoint(pos):
            return CardSelectionResult(self.request.request_id, [], skipped=True)

        for instance_id, rect in self.card_rects.items():
            if rect.collidepoint(pos):
                self.toggle(instance_id)
                return None

        next_rect = pygame.Rect(self.rect.right - 85, self.rect.y + 72, 44, 34)
        prev_rect = pygame.Rect(self.rect.right - 140, self.rect.y + 72, 44, 34)
        if next_rect.collidepoint(pos):
            self.next_page()
        elif prev_rect.collidepoint(pos):
            self.prev_page()
        return None

    def toggle(self, instance_id: str) -> None:
        if instance_id in self.selected_ids:
            self.selected_ids.remove(instance_id)
            return
        max_count = self.request.exact_count or self.request.max_count
        if len(self.selected_ids) >= max_count:
            # 1枚選択のときはクリックで入れ替える。
            if max_count == 1:
                self.selected_ids.clear()
            else:
                return
        self.selected_ids.add(instance_id)

    def can_confirm(self) -> bool:
        if not self.candidates:
            return True
        count = len(self.selected_ids)
        if self.request.exact_count is not None:
            return count == self.request.exact_count
        return self.request.min_count <= count <= self.request.max_count

    def result(self) -> CardSelectionResult:
        skipped = not self.selected_ids and not self.candidates
        return CardSelectionResult(
            request_id=self.request.request_id,
            selected_instance_ids=list(self.selected_ids),
            skipped=skipped,
        )

    def page_candidates(self) -> list[CardSelectionCandidate]:
        start = self.page * self.cards_per_page
        end = start + self.cards_per_page
        return self.candidates[start:end]

    def max_page(self) -> int:
        if not self.candidates:
            return 0
        return max(0, (len(self.candidates) - 1) // self.cards_per_page)

    def next_page(self) -> None:
        self.page = min(self.max_page(), self.page + 1)

    def prev_page(self) -> None:
        self.page = max(0, self.page - 1)

    def draw(self, surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, colors.PANEL, self.rect, border_radius=16)
        pygame.draw.rect(surface, colors.GOLD, self.rect, width=2, border_radius=16)

        draw_text(surface, self.request.title, get_font(32, bold=True), colors.GOLD, (self.rect.x + 28, self.rect.y + 22))
        message_rect = pygame.Rect(self.rect.x + 28, self.rect.y + 62, self.rect.width - 220, 56)
        draw_wrapped(surface, self.request.message, get_font(18), colors.TEXT, message_rect)

        draw_text(
            surface,
            f"選択 {len(self.selected_ids)} / {self.request.exact_count or self.request.max_count}",
            get_font(18, bold=True),
            colors.TEXT,
            (self.rect.right - 215, self.rect.y + 28),
        )
        draw_text(
            surface,
            f"{self.page + 1}/{self.max_page() + 1}",
            get_font(16),
            colors.MUTED,
            (self.rect.right - 132, self.rect.y + 80),
        )

        pygame.draw.rect(surface, colors.PANEL_LIGHT, (self.rect.right - 140, self.rect.y + 72, 44, 34), border_radius=8)
        pygame.draw.rect(surface, colors.PANEL_LIGHT, (self.rect.right - 85, self.rect.y + 72, 44, 34), border_radius=8)
        draw_text(surface, "<", get_font(20, bold=True), colors.TEXT, (self.rect.right - 118, self.rect.y + 89), center=True)
        draw_text(surface, ">", get_font(20, bold=True), colors.TEXT, (self.rect.right - 63, self.rect.y + 89), center=True)

        self.card_rects.clear()
        page_candidates = self.page_candidates()
        if not page_candidates:
            draw_text(surface, "対象カードがありません。", get_font(26, bold=True), colors.MUTED, self.rect.center, center=True)
        else:
            card_w, card_h = 150, 210
            gap = 24
            total_w = len(page_candidates) * (card_w + gap) - gap
            start_x = self.rect.centerx - total_w // 2
            y = self.rect.y + 165
            mouse = pygame.mouse.get_pos()
            for i, candidate in enumerate(page_candidates):
                card = candidate.card
                rect = pygame.Rect(start_x + i * (card_w + gap), y, card_w, card_h)
                self.card_rects[card.instance_id] = rect
                view = CardView(self.registry, rect, card, enabled=True)
                view.handle_motion(mouse)
                view.draw(surface)
                label_rect = pygame.Rect(rect.x, rect.bottom + 6, rect.width, 24)
                draw_text(surface, ZONE_LABELS.get(candidate.zone, candidate.zone), get_font(14), colors.MUTED, label_rect.center, center=True)
                if card.instance_id in self.selected_ids:
                    pygame.draw.rect(surface, colors.GOLD, rect.inflate(8, 8), width=4, border_radius=14)

        self.confirm_button.enabled = self.can_confirm()
        self.confirm_button.draw(surface)
        if self.request.allow_skip:
            self.skip_button.draw(surface)
