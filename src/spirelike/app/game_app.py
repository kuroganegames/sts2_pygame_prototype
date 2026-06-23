from __future__ import annotations

from pathlib import Path
import pygame

from spirelike.app.settings import Settings
from spirelike.app.scene_manager import SceneManager
from spirelike.content.loader import ContentLoader
from spirelike.scenes.title_scene import TitleScene
from spirelike.scenes.character_select_scene import CharacterSelectScene
from spirelike.scenes.map_scene import MapScene
from spirelike.scenes.combat_scene import CombatScene
from spirelike.scenes.reward_scene import RewardScene
from spirelike.scenes.rest_scene import RestScene
from spirelike.scenes.event_scene import EventScene
from spirelike.scenes.shop_scene import ShopScene
from spirelike.scenes.run_result_scene import RunResultScene


class GameApp:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.settings = Settings()
        self.running = True
        self.run_state = None

        pygame.init()
        pygame.display.set_caption(self.settings.title)
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        self.clock = pygame.time.Clock()

        content_dir = project_root / self.settings.content_dir_name
        self.registry = ContentLoader(content_dir).load()

        self.scene_manager = SceneManager(self)
        self._register_scenes()
        self.scene_manager.change("title")

    def _register_scenes(self) -> None:
        self.scene_manager.register("title", lambda app, payload: TitleScene(app, payload))
        self.scene_manager.register(
            "character_select", lambda app, payload: CharacterSelectScene(app, payload)
        )
        self.scene_manager.register("map", lambda app, payload: MapScene(app, payload))
        self.scene_manager.register("combat", lambda app, payload: CombatScene(app, payload))
        self.scene_manager.register("reward", lambda app, payload: RewardScene(app, payload))
        self.scene_manager.register("rest", lambda app, payload: RestScene(app, payload))
        self.scene_manager.register("event", lambda app, payload: EventScene(app, payload))
        self.scene_manager.register("shop", lambda app, payload: ShopScene(app, payload))
        self.scene_manager.register("run_result", lambda app, payload: RunResultScene(app, payload))

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(self.settings.fps) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.scene_manager.handle_event(event)

            self.scene_manager.update(dt)
            self.scene_manager.draw(self.screen)
            pygame.display.flip()

        pygame.quit()

    def quit(self) -> None:
        self.running = False
