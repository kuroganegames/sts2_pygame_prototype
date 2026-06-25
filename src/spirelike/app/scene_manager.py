from __future__ import annotations

from typing import Callable, Dict, Optional, Any


class SceneManager:
    def __init__(self, app: "GameApp") -> None:
        self.app = app
        self._factories: Dict[str, Callable[["GameApp", dict], object]] = {}
        self.current_scene: Optional[object] = None
        self.current_name: Optional[str] = None

    def register(self, name: str, factory: Callable[["GameApp", dict], object]) -> None:
        self._factories[name] = factory

    def change(self, name: str, payload: Optional[dict[str, Any]] = None) -> None:
        if name not in self._factories:
            raise KeyError(f"Scene is not registered: {name}")
        payload = payload or {}
        self.current_name = name
        self.current_scene = self._factories[name](self.app, payload)
        if hasattr(self.app, "autosave_if_possible"):
            self.app.autosave_if_possible(name, payload)

    def handle_event(self, event) -> None:
        if self.current_scene is not None:
            self.current_scene.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def draw(self, surface) -> None:
        if self.current_scene is not None:
            self.current_scene.draw(surface)
