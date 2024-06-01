import traceback

from sqlalchemy.exc import SQLAlchemyError

from ..app import db
from ..models.plex_data_models import (
    Album,
    Artist,
    Episode,
    Movie,
    Photo,
    Playlist,
    PlaylistType,
    Season,
    Show,
    Track,
)
from ..utils.logging import LOGGER
from .data import get_playlist_data


def store_playlist_data(playlist_data):
    try:
        for playlist_type_name, playlists in playlist_data.items():
            playlist_type = PlaylistType.query.filter_by(name=playlist_type_name).first()
            if not playlist_type:
                playlist_type = PlaylistType(name=playlist_type_name)
                db.session.add(playlist_type)

            for playlist_title, items in playlists.items():
                playlist = Playlist.query.filter_by(
                    name=playlist_title, playlist_type_id=playlist_type.id
                ).first()
                if not playlist:
                    playlist = Playlist(name=playlist_title, playlist_type=playlist_type)
                    db.session.add(playlist)

                if playlist_type_name == "audio":
                    store_audio_playlist(items, playlist)
                elif playlist_type_name == "video":
                    store_video_playlist(items, playlist)
                elif playlist_type_name == "photo":
                    store_photo_playlist(items, playlist)

        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        error_info = traceback.format_exc()
        LOGGER.error(f"Failed to store playlist data: {error_info}")


def create_or_get_artist(artist_name):
    if not artist_name:
        LOGGER.error(f"Invalid artist name: {artist_name}")
        return None
    artist = Artist.query.filter_by(name=artist_name).first()
    if not artist:
        artist = Artist(name=artist_name)
        db.session.add(artist)
        db.session.flush()
    return artist


def create_or_get_album(album_title, artist):
    if not album_title:
        LOGGER.error(f"Invalid album title: {album_title}")
        return None
    album = Album.query.filter_by(title=album_title, artist_id=artist.id).first()
    if not album:
        album = Album(title=album_title, artist=artist)
        db.session.add(album)
        db.session.flush()
    return album


def create_or_update_track(track_data, album, artist):
    track_title = track_data.get("title")
    track_number = track_data.get("number")
    if not track_title or track_number is None:
        LOGGER.error(f"Invalid track data: {track_data}")
        return None
    track = Track.query.filter_by(title=track_title, album_id=album.id, artist_id=artist.id).first()
    if not track:
        track = Track(
            title=track_title,
            number=track_number,
            album_id=album.id,
            artist_id=artist.id,
        )
        db.session.add(track)
    elif track.number != track_number:
        track.number = track_number
        db.session.add(track)
    return track


def add_item_to_playlist(playlist, item):
    if item and item not in playlist.items:
        playlist.items.append(item)


def store_audio_playlist(data, playlist):
    for artist_name, artist_data in data["artists"].items():
        artist = create_or_get_artist(artist_name)
        if not artist:
            continue

        for album_title, album_data in artist_data["albums"].items():
            album = create_or_get_album(album_title, artist)
            if not album:
                continue

            for track_data in album_data["tracks"]:
                track = create_or_update_track(track_data, album, artist)
                add_item_to_playlist(playlist, track)


def store_video_playlist(data, playlist):
    for show_title, show_data in data["shows"].items():
        store_show_data(show_title, show_data, playlist)
    for movie_data in data["movies"]:
        store_movie_data(movie_data, playlist)


def store_show_data(show_title, show_data, playlist):
    if not show_title:
        LOGGER.error(f"Invalid show title: {show_title}")
        return

    show = Show.query.filter_by(title=show_title).first()
    if not show:
        show = Show(title=show_title)
        db.session.add(show)

    for season_title, season_data in show_data["seasons"].items():
        store_season_data(season_title, season_data, show, playlist)


def store_season_data(season_title, season_data, show, playlist):
    if not season_title:
        LOGGER.error(f"Invalid season title: {season_title}")
        return

    season = Season.query.filter_by(title=season_title, show_id=show.id).first()
    if not season:
        season = Season(title=season_title, show_id=show.id)
        db.session.add(season)

    for episode_data in season_data["episodes"]:
        store_episode_data(episode_data, season, show, playlist)


def store_episode_data(episode_data, season, show, playlist):
    episode_title = episode_data["title"]
    if not episode_title:
        LOGGER.error(f"Invalid episode title: {episode_title}")
        return

    episode = Episode.query.filter_by(
        title=episode_title, season_id=season.id, show_id=show.id
    ).first()
    if not episode:
        episode = Episode(title=episode_title, season_id=season.id, show_id=show.id)
        db.session.add(episode)
    add_item_to_playlist(playlist, episode)


def store_movie_data(movie_data, playlist):
    movie_title = movie_data["title"]
    movie_year = movie_data["year"]
    if not movie_title:
        LOGGER.error(f"Invalid movie title: {movie_title}")
        return

    movie = Movie.query.filter_by(title=movie_title, year=movie_year).first()
    if not movie:
        movie = Movie(title=movie_title, year=movie_year)
        db.session.add(movie)
    add_item_to_playlist(playlist, movie)


def store_photo_playlist(data, playlist):
    for photo_data in data["photos"]:
        photo_title = photo_data["title"]
        if not photo_title:
            LOGGER.error(f"Invalid photo title: {photo_title}")
            continue

        photo = Photo.query.filter_by(title=photo_title).first()
        if not photo:
            photo = Photo(title=photo_title, file_path=photo_data["path"])
            db.session.add(photo)
        add_item_to_playlist(playlist, photo)


def get_and_store_playlist_data():
    playlist_data = get_playlist_data()
    store_playlist_data(playlist_data)
