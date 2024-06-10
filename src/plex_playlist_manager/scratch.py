import os
import random

from flask import current_app
from plexapi.server import PlexServer
from sqlalchemy import asc

# from .app import app
# from .database import db
# from .models.plex_data_models import Album, Playlist, PlaylistType, Track
# from .models.plex_data_models import Album, Playlist, PlaylistType, Track
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
            for item in playlist.items():
                print(item.grandparentTitle)


def test2():
    playlist_data = get_playlist_data(plex_server)
    for playlist_type, playlist_list in playlist_data.items():
        print(f"{playlist_type.capitalize()} playlists:")
        if playlist_type == "audio":
            for playlist, playlist_data in playlist_list.items():
                print(f"\t{playlist}")
                for artist, albums in playlist_data.items():
                    print(f"\t\t{artist}")
                    for album, tracks in albums.items():
                        print(f"\t\t\t{album}")
                        for track in tracks:
                            print(f"\t\t\t\t{track[1]}: {track[0]}")
        if playlist_type == "video":
            for playlist, playlist_data in playlist_list.items():
                print(f"\t{playlist}")
                for title in playlist_data:
                    if title == "Episode":
                        for show, season in playlist_data[title].items():
                            print(f"\t\ {show}")
                            for season_number, episodes in season.items():
                                print(f"\t\t\tseason: {season_number}")
                                for episode in episodes:
                                    print(f"\t\t\t\t{episode[1]}: {episode[0]}")

                    if title == "Movie":
                        for movie, year in playlist_data[title].items():
                            print(f"\t\t{movie} ({year})")


def test3():
    name = "Zeppelin"
    with app.app_context():
        playlist = db.session.query(Playlist).filter_by(title=name).first()
        if playlist:
            print(f"Playlist: {playlist.title}")
            print("Artists:")
            for artist in playlist.artists:
                print(artist.name)  # replace with the actual attribute of Artist
        #     print("Movies:")
        #     for movie in playlist.movies:
        #         print(movie.title)  # replace with the actual attribute of Movie
        #     print("Shows:")
        #     for show in playlist.shows:
        #         print(show.title)  # replace with the actual attribute of Show
        #     print("Photos:")
        #     for photo in playlist.photos:
        #         print(photo.title)  # replace with the actual attribute of Photo
        # else:
        #     print("No playlist found with that name.")


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
    # app.config["RECREATE_DB_ON_START"] = True
    with app.app_context():
        playlist_types = db.session.query(PlaylistType).all()
        playlists_by_type = {}
        for playlist_type in playlist_types:
            # print(playlist_type.name)
            playlists_by_type[playlist_type.name] = (
                db.session.query(Playlist).filter_by(playlist_type_id=playlist_type.id).all()
            )
        # playlist = db.session.query(Playlist).first()
        for playlist_type, playlists in playlists_by_type.items():
            if playlist_type == "audio":
                for playlist in playlists:
                    if playlist.name == "Shower Songs":
                        print(f"Playlist: {playlist.name}")
                        grouped_items = playlist.get_items_grouped_by_artist_album()
                        for artist, _albums in grouped_items.items():
                            print(f"\t{artist}")
                            # for album, tracks in albums.items():
                            #     print(f"\t\t\tAlbum: {album}")
                            #     for track in tracks:
                            #         print(f"\t\t\t\tTrack: {track.number}: {track.title}")


def test6():
    with app.app_context():
        playlist = db.session.query(Playlist).filter_by(name="Shower Songs").first()
        if playlist:
            print(f"Playlist: {playlist.name}")
            grouped_items = playlist.get_items_grouped_by_artist_album()
            for artist, _albums in grouped_items.items():
                print(f"\t{artist}")
