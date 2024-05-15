import os
import sys
from pathlib import Path

from .utils.logging import setup_logger

media_conveyor_root = Path.home() / ".plex_cred"
project_root = Path(__file__).resolve().parent.parent.parent
os.environ["PLEX_CRED"] = str(project_root / "tests/.plex_cred")


def main():
    setup_logger()
    os.environ["FLASK_APP"] = "plex_playlist_manager.flask.app"
    os.environ["FLASK_ENV"] = "development"
    sys.argv = ["flask", "run"]
    os.system(" ".join(sys.argv))
