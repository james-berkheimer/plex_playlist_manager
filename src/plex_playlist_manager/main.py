import os
from pathlib import Path

from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer

from .authentication import PlexAuthentication
from .logging import setup_logger

media_conveyor_root = Path.home() / ".plex_cred"
project_root = Path(__file__).resolve().parent.parent.parent
os.environ["PLEX_CRED"] = str(project_root / "tests/.plex_cred")


def main():
    """Main entry point for the application script"""
    setup_logger()
    plex_auth = PlexAuthentication()
    plex = plex = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)
    playlists = plex.playlists()
    audio_playlists = [playlist for playlist in playlists if playlist.playlistType == "audio"]
    for playlist in audio_playlists:
        playlist_data = playlist_data_dict(playlist)
        print(playlist.title)
        for artist in playlist_data[playlist.title]:
            print(f"\t{artist}")
            for album in playlist_data[playlist.title][artist]:
                print(f"\t\t{album}")
                for track in playlist_data[playlist.title][artist][album]:
                    print(f"\t\t\t{track[0]}: {track[1]}")

        # for artist in playlist_data["Test"]:
        #     print(artist)
        #     for album in playlist_data["Test"][artist]:
        #         print(f"\t{album}")
        #         for track in playlist_data["Test"][artist][album]:
        #             print(f"\t\t{track[0]}: {track[1]}")

    # test_playlist = next((playlist for playlist in playlists if playlist.title == "Test"), None)
    # playlist_data = playlist_data_dict(test_playlist)
    # for artist in playlist_data["Test"]:
    #     print(artist)
    #     for album in playlist_data["Test"][artist]:
    #         print(f"\t{album}")
    #         for track in playlist_data["Test"][artist][album]:
    #             print(f"\t\t{track[0]}: {track[1]}")


def playlist_data_dict(playlist):
    """Return a dictionary of playlist data"""
    if playlist.playlistType != "audio":
        return None

    playlist_data = {
        playlist.title: {},
    }
    for item in playlist.items():
        artist = item.grandparentTitle
        album = item.parentTitle
        track = item.title
        track_number = item.trackNumber  # assuming the item object has a trackNumber attribute

        if artist not in playlist_data[playlist.title]:
            playlist_data[playlist.title][artist] = {}

        if album not in playlist_data[playlist.title][artist]:
            playlist_data[playlist.title][artist][album] = []

        playlist_data[playlist.title][artist][album].append((track_number, track))

    return playlist_data
