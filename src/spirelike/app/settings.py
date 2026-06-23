from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    screen_width: int = 1280
    screen_height: int = 720
    fps: int = 60
    title: str = "STS2 Pygame Prototype"
    hand_size: int = 5
    max_hand_size: int = 10
    card_width: int = 132
    card_height: int = 184
    content_dir_name: str = "content"
