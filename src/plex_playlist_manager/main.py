import os
from pathlib import Path

from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer
from PyQt6.QtWidgets import QApplication

from .authentication import PlexAuthentication
from .guis.playlist_gui import PlaylistGUI
from .logging import setup_logger

media_conveyor_root = Path.home() / ".plex_cred"
project_root = Path(__file__).resolve().parent.parent.parent
os.environ["PLEX_CRED"] = str(project_root / "tests/.plex_cred")


# Assuming playlist_data is the data you got from the previous script
# run_app(playlist_data)


# def playlist_data_dict(playlist):
#     """Return a dictionary of playlist data"""
#     if playlist.playlistType != "audio":
#         return None

#     playlist_data = {
#         playlist.title: {},
#     }
#     for item in playlist.items():
#         artist = item.grandparentTitle
#         album = item.parentTitle
#         track = item.title
#         track_number = item.trackNumber  # assuming the item object has a trackNumber attribute

#         if artist not in playlist_data[playlist.title]:
#             playlist_data[playlist.title][artist] = {}

#         if album not in playlist_data[playlist.title][artist]:
#             playlist_data[playlist.title][artist][album] = []

#         playlist_data[playlist.title][artist][album].append((track_number, track))

#     return playlist_data


def main():
    """Main entry point for the application script"""
    setup_logger()
    app = QApplication([])

    plex_auth = PlexAuthentication()
    plex_server = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)
    playlist_gui = PlaylistGUI(plex_server)

    playlist_gui.show()
    app.exec()
