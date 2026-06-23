from __future__ import annotations

import pygame


class BaseScene:
    def __init__(self, app, payload: dict) -> None:
        self.app = app
        self.payload = payload
        self.buttons = []

    def handle_event(self, event) -> None:
        for button in list(self.buttons):
            if button.handle_event(event):
                return

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass
