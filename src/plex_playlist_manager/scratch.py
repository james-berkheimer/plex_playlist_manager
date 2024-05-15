import os
import random
from pathlib import Path
from pprint import pprint

from flask import Flask, render_template
from plexapi.exceptions import BadRequest, NotFound
from plexapi.server import PlexServer
from PyQt6.QtWidgets import QApplication

from .gui.playlist_gui import PlaylistGUI
from .utils.authentication import PlexAuthentication
from .utils.logging import setup_logger

media_conveyor_root = Path.home() / ".plex_cred"
project_root = Path(__file__).resolve().parent.parent.parent
os.environ["PLEX_CRED"] = str(project_root / "tests/.plex_cred")


plex_auth = PlexAuthentication()
plex = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)


def get_playlists(playlists):
    try:
        categorized_playlists = {"audio": [], "video": [], "photo": []}
        for playlist in playlists:
            if playlist.playlistType in categorized_playlists:
                categorized_playlists[playlist.playlistType].append(playlist)
        return categorized_playlists
    except Exception as e:
        print(f"Failed to fetch playlists: {e}")
        return {"audio": [], "video": [], "photo": []}


def get_playlist_audio_data(playlists):
    all_playlist_data = {}
    for playlist in playlists["audio"]:
        print(f"playlist: {playlist.title}")
        playlist_title = playlist.title.strip()
        playlist_data = {playlist_title: {}}

        for item in playlist.items():
            artist = item.grandparentTitle.strip()
            album = item.parentTitle.strip()
            track = item.title.strip()
            track_number = item.trackNumber

            artist_albums = playlist_data[playlist_title].setdefault(artist, {})
            album_tracks = artist_albums.setdefault(album, [])
            album_tracks.append((track_number, track))

        all_playlist_data.update(playlist_data)  # Add this playlist's data to the main dictionary

    return all_playlist_data


def main():
    """Main entry point for the application script"""
    setup_logger()
    app = QApplication([])

    plex_auth = PlexAuthentication()
    plex_server = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)
    playlist_gui = PlaylistGUI(plex_server)

    playlist_gui.show()
    app.exec()


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


def test3():
    artists = plex.search("Led Zeppelin", mediatype="artist")
    if artists:
        led_zeppelin = artists[0]  # Assuming the first result is the correct artist
        songs = led_zeppelin.tracks()  # Get all tracks by Led Zeppelin
        playlist_songs = random.sample(songs, 3)  # Select 3 random songs
        print(playlist_songs)
        plex.createPlaylist("Test Playlist", items=playlist_songs)
        playlists = plex.playlists()
    for playlist in playlists:
        print(playlist.title)
    else:
        print("Artist not found")


def flask_run():
    app = Flask(__name__)

    app.run(debug=True)  # debug=True will provide more detailed error messages
