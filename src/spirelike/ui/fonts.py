from __future__ import annotations

from functools import lru_cache
import pygame


FONT_CANDIDATES = [
    "Yu Gothic",
    "YuGothic",
    "Meiryo",
    "Noto Sans CJK JP",
    "Noto Sans JP",
    "Hiragino Sans",
    "Hiragino Kaku Gothic ProN",
    "Arial Unicode MS",
    "DejaVu Sans",
    "Arial",
]


@lru_cache(maxsize=64)
def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont(FONT_CANDIDATES, size, bold=bold)
