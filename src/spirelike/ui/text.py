from __future__ import annotations

import pygame


def draw_text(surface, text: str, font, color, pos, *, center: bool = False) -> pygame.Rect:
    image = font.render(str(text), True, color)
    rect = image.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(image, rect)
    return rect


def wrap_text(text: str, font, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).split("\n"):
        current = ""
        for ch in paragraph:
            candidate = current + ch
            if font.size(candidate)[0] <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines or [""]


def draw_wrapped(surface, text: str, font, color, rect: pygame.Rect, line_gap: int = 3) -> None:
    y = rect.y
    for line in wrap_text(text, font, rect.width):
        if y + font.get_height() > rect.bottom:
            break
        image = font.render(line, True, color)
        surface.blit(image, (rect.x, y))
        y += font.get_height() + line_gap
