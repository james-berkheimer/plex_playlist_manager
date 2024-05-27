import os
import random

from flask import current_app
from plexapi.server import PlexServer
from sqlalchemy import asc

from .app import app
from .database import db
from .models.plex_data_models import Playlist, PlaylistType
from .plex.authentication import PlexAuthentication
from .plex.scratch_data import (
    categorize_playlists,
    get_playlist_audio_data,
    get_playlist_data,
    get_playlist_video_data,
)

os.environ["PLEX_CRED"] = "/home/james/code/flask_test/tests/.plex_cred"


plex_auth = PlexAuthentication()
plex_server = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)


MEDIA_TYPES = ["plexapi.video.Episode", "plexapi.video.Movie", "plexapi.audio.Track"]


def test1():
    playlists = plex_server.playlists()
    categorized_playlists = categorize_playlists(playlists)
    for playlist_type, playlist_list in categorized_playlists.items():
        print(f"{playlist_type.capitalize()} playlists:")
        for playlist in playlist_list:
            print(f"\t{playlist.title}")


def test2():
    playlists = plex_server.playlists()
    categorized_playlists = categorize_playlists(playlists)
    video_data = get_playlist_video_data(categorized_playlists["video"])
    for key, value in video_data.items():
        print(key)
        for k, v in value.items():
            print(f"\t{k}")
            if isinstance(v, dict):
                for i, p in v.items():
                    print(f"\t\t{i}")
                    for item in p:
                        print(f"\t\t\t{item[1]}")
            else:
                print(f"\t\t{v}")


def test3():
    artists = plex_server.search("Led Zeppelin", mediatype="artist")
    if artists:
        led_zeppelin = artists[0]  # Assuming the first result is the correct artist
        songs = led_zeppelin.tracks()  # Get all tracks by Led Zeppelin
        playlist_songs = random.sample(songs, 3)  # Select 3 random songs
        print(playlist_songs)
        plex_server.createPlaylist("Test Playlist", items=playlist_songs)
        playlists = plex_server.playlists()
    for playlist in playlists:
        print(playlist.title)
    else:
        print("Artist not found")


def test4():
    with app.app_context():
        playlist_types = db.session.query(PlaylistType).all()
        playlists_by_type = {}
        for playlist_type in playlist_types:
            playlists_by_type[playlist_type.name] = (
                db.session.query(Playlist).filter_by(playlist_type_id=playlist_type.id).all()
            )
        for playlist_type, playlists in playlists_by_type.items():
            print(f"{playlist_type.capitalize()} playlists:")
            for playlist in playlists:
                print(f"\t{playlist.title}")


def test5():
    playlist_data = get_playlist_data(plex_server)
    for _playlist_type, playlists in playlist_data.items():
        for _playlist_name, playlist in playlists.items():
            for artist, albums in playlist.get("artists", {}).items():
                if artist == "38 Special":
                    print(f"create_artist({artist}, new_playlist)")
                    for album, tracks in albums["albums"].items():
                        print(f"\tcreate_album({album}, new_artist)")
                        for track in tracks["tracks"]:
                            print(
                                f"\t\tcreate_track({track['title']}, {track['number']}, new_album)"
                            )


def test6():
    playlist_data = get_playlist_data(plex_server)
    for playlist_type, playlists in playlist_data.items():
        for playlist_name, playlist in playlists.items():
            print(f"Create new playlist: {playlist_name, playlist_type}")
            for artist, albums in playlist.get("artists", {}).items():
                print(f"\tcreate_artist({artist}, new_playlist)")
                for album, tracks in albums["albums"].items():
                    print(f"\t\tcreate_album({album}, new_artist)")
                    for track in tracks["tracks"]:
                        print(f"\t\t\tcreate_track({track['title']}, {track['number']}, new_album)")
            for show, seasons in playlist.get("shows", {}).items():
                print(f"\tcreate_show({show}, new_playlist)")
                for season, episodes in seasons["seasons"].items():
                    print(f"\t\tcreate_season({season}, new_show)")
                    for episode in episodes["episodes"]:
                        print(
                            f"\t\t\tcreate_episode({episode['title']}, {episode['number']}, new_season)"
                        )
            for movie in playlist.get("movies", []):
                print(f"\tcreate_movie({movie['title']}, {movie['year']}, new_playlist)")
