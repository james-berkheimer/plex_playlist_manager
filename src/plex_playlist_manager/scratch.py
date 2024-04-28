import os
from pathlib import Path
from pprint import pprint

from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer

from .authentication import PlexAuthentication

media_conveyor_root = Path.home() / ".plex_cred"
project_root = Path(__file__).resolve().parent.parent.parent
os.environ["PLEX_CRED"] = str(project_root / "tests/.plex_cred")


plex_auth = PlexAuthentication()
plex = plex = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)


def get_playlists(playlists):
    try:
        categorized_playlists = {
            "audio": [playlist for playlist in playlists if playlist.playlistType == "audio"],
            "video": [playlist for playlist in playlists if playlist.playlistType == "video"],
            "photo": [playlist for playlist in playlists if playlist.playlistType == "photo"],
        }
        return categorized_playlists
    except Exception as e:
        print(f"Failed to fetch playlists: {e}")
        return {"audio": [], "video": [], "photo": []}


def get_playlist_audio_data(playlists):
    all_playlist_data = {}  # Initialize the dictionary outside of the loop
    for playlist in playlists["audio"]:
        print(f"playlist: {playlist.title}")
        playlist_data = {
            playlist.title.strip(): {},  # Strip whitespace from the title
        }
        for item in playlist.items():
            artist = item.grandparentTitle.strip()  # Strip whitespace from the artist name
            album = item.parentTitle.strip()  # Strip whitespace from the album name
            track = item.title.strip()  # Strip whitespace from the track name
            track_number = item.trackNumber

            if artist not in playlist_data[playlist.title.strip()]:
                playlist_data[playlist.title.strip()][artist] = {}

            if album not in playlist_data[playlist.title.strip()][artist]:
                playlist_data[playlist.title.strip()][artist][album] = []

            playlist_data[playlist.title.strip()][artist][album].append((track_number, track))

        all_playlist_data.update(playlist_data)  # Add this playlist's data to the main dictionary

    return all_playlist_data


def test1():
    playlists = plex.playlists()
    categorized_playlists = get_playlists(playlists)
    for playlist_type, playlist_list in categorized_playlists.items():
        print(f"{playlist_type.capitalize()} playlists:")
        for playlist in playlist_list:
            print(f"\t{playlist.title}")


def test2():
    playlists = plex.playlists()
    categorized_playlists = get_playlists(playlists)
    audio_data = get_playlist_audio_data(categorized_playlists)
    print(audio_data.keys())
    for playlist_title, playlist_data in audio_data.items():
        print(f"{playlist_title}:")
        for artist, albums in playlist_data.items():
            print(f"\t{artist}")
            for album, tracks in albums.items():
                print(f"\t\t{album}")
                for track in tracks:
                    print(f"\t\t\t{track[0]}: {track[1]}")
