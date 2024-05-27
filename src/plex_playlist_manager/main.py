import os
import sys

import click

from .utils.logging import LOGGER


@click.command()
@click.option("-d", "--debugger", is_flag=True, help="Runs the server with debugger.")
def main(debugger):
    LOGGER.info("Starting Plex Playlist Manager")
    os.environ["FLASK_APP"] = "plex_playlist_manager.app"
    os.environ["PLEX_CRED"] = "/home/james/code/flask_test/tests/.plex_cred"

    if debugger:
        os.environ["FLASK_DEBUG"] = "1"
    os.system("flask run")

    sys.argv = ["flask", "run"]
    os.system(" ".join(sys.argv))
