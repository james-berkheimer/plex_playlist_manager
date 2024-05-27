from ..app import db
from ..models.plex_data_models import (
    Album,
    Artist,
    Episode,
    Movie,
    Playlist,
    Season,
    Show,
    Track,
)
from ..utils.logging import LOGGER
from .data import get_playlist_data


def create_playlist(playlist, playlist_type):
    new_playlist = Playlist(title=playlist["title"], type=playlist_type)
    db.session.add(new_playlist)
    return new_playlist


def create_artist(artist, playlist):
    new_artist = Artist(name=artist["name"])
    db.session.add(new_artist)
    playlist.artists.append(new_artist)
    return new_artist


def create_album(album, artist):
    new_album = Album(title=album["title"], artist=artist)
    db.session.add(new_album)
    return new_album


def create_track(track, album):
    new_track = Track(title=track["title"], number=track["number"], album=album)
    db.session.add(new_track)
    return new_track


def create_show(show, playlist):
    new_show = Show(title=show["title"])
    db.session.add(new_show)
    playlist.shows.append(new_show)
    return new_show


def create_season(season, show):
    new_season = Season(title=season["title"], show=show)
    db.session.add(new_season)
    return new_season


def create_episode(episode, season):
    new_episode = Episode(title=episode["title"], number=episode["number"], season=season)
    db.session.add(new_episode)
    return new_episode


def create_movie(movie, playlist):
    new_movie = Movie(title=movie["title"], year=movie["year"])
    db.session.add(new_movie)
    playlist.movies.append(new_movie)
    return new_movie


def store_playlist_data():
    LOGGER.info("Storing playlist data...")
    playlist_data = get_playlist_data()

    for playlist_type, playlists in playlist_data.items():
        for playlist_name, playlist in playlists.items():
            LOGGER.debug(f"Creating playlist: {playlist_name}")
            new_playlist = create_playlist({"title": playlist_name}, playlist_type)

            for artist_name, artist_data in playlist.get("artists", {}).items():
                LOGGER.debug(f"Creating artist: {artist_name}")
                new_artist = create_artist({"name": artist_name}, new_playlist)
                for album_name, album_data in artist_data["albums"].items():
                    LOGGER.debug(f"Creating album: {album_name}")
                    new_album = create_album({"title": album_name}, new_artist)
                    for track in album_data["tracks"]:
                        LOGGER.debug(f"Creating track: {track['title']}")
                        create_track(
                            {"title": track["title"], "number": track["number"]}, new_album
                        )

            for show_name, show_data in playlist.get("shows", {}).items():
                LOGGER.debug(f"Creating show: {show_name}")
                new_show = create_show({"title": show_name}, new_playlist)
                for season_name, season_data in show_data["seasons"].items():
                    LOGGER.debug(f"Creating season: {season_name}")
                    new_season = create_season({"title": season_name}, new_show)
                    for episode in season_data["episodes"]:
                        LOGGER.debug(f"Creating episode: {episode['title']}")
                        create_episode(
                            {"title": episode["title"], "number": episode["number"]}, new_season
                        )

            for movie in playlist.get("movies", []):
                LOGGER.debug(f"Creating movie: {movie['title']}")
                create_movie({"title": movie["title"], "year": movie["year"]}, new_playlist)

    db.session.commit()
    LOGGER.info("Playlist data stored successfully.")
