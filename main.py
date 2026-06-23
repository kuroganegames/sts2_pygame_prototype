from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from spirelike.app.game_app import GameApp


if __name__ == "__main__":
    GameApp(project_root=ROOT).run()
