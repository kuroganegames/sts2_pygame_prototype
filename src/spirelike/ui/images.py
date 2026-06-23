from __future__ import annotations

from pathlib import Path
from typing import Optional
import pygame


class ImageCache:
    def __init__(self) -> None:
        self._cache: dict[tuple[str, tuple[int, int] | None], pygame.Surface] = {}

    def load(self, path: Optional[Path], size: tuple[int, int] | None = None) -> pygame.Surface:
        key = (str(path) if path else "__missing__", size)
        if key in self._cache:
            return self._cache[key]
        if path and Path(path).exists():
            image = pygame.image.load(str(path)).convert_alpha()
        else:
            image = pygame.Surface(size or (128, 128), pygame.SRCALPHA)
            image.fill((80, 80, 90))
        if size:
            image = pygame.transform.smoothscale(image, size)
        self._cache[key] = image
        return image


image_cache = ImageCache()
