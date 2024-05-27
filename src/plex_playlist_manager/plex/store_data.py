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
from .data_validation import (
    validate_album,
    validate_artist,
    validate_episode,
    validate_movie,
    validate_photo,
    validate_playlist,
    validate_playlist_type,
    validate_season,
    validate_show,
    validate_track,
)


def create_playlist_type(playlist_type_name):
    validate_playlist_type(playlist_type_name)
    existing_playlist_type = PlaylistType.query.filter_by(name=playlist_type_name).first()
    if existing_playlist_type:
        return existing_playlist_type
    new_playlist_type = PlaylistType(name=playlist_type_name)
    db.session.add(new_playlist_type)
    db.session.commit()
    return new_playlist_type


def create_playlist(playlist, playlist_type):
    validate_playlist(playlist)
    existing_playlist = Playlist.query.filter_by(title=playlist["title"]).first()
    if existing_playlist:
        return existing_playlist
    new_playlist = Playlist(
        title=playlist["title"],
        playlist_type_name=playlist_type.name,
        playlist_type_id=playlist_type.id,
    )
    db.session.add(new_playlist)
    return new_playlist


def create_artist(artist, playlist):
    validate_artist(artist)
    existing_artist = Artist.query.filter_by(name=artist["name"]).first()
    if existing_artist:
        return existing_artist
    new_artist = Artist(name=artist["name"])
    db.session.add(new_artist)
    playlist.artists.append(new_artist)
    return new_artist


def create_album(album, artist):
    validate_album(album)
    existing_album = Album.query.filter_by(title=album["title"], artist_id=artist.id).first()
    if existing_album:
        return existing_album
    new_album = Album(title=album["title"], artist=artist)
    db.session.add(new_album)
    return new_album


def create_track(track, album):
    validate_track(track)
    existing_track = Track.query.filter_by(title=track["title"], album_id=album.id).first()
    if existing_track:
        return existing_track
    new_track = Track(title=track["title"], number=track["number"], album=album)
    db.session.add(new_track)
    return new_track


def create_show(show, playlist):
    validate_show(show)
    existing_show = Show.query.filter_by(title=show["title"]).first()
    if existing_show:
        return existing_show
    new_show = Show(title=show["title"])
    db.session.add(new_show)
    playlist.shows.append(new_show)
    return new_show


def create_season(season, show):
    validate_season(season)
    existing_season = Season.query.filter_by(title=season["title"], show_id=show.id).first()
    if existing_season:
        return existing_season
    new_season = Season(title=season["title"], show=show)
    db.session.add(new_season)
    return new_season


def create_episode(episode, season):
    validate_episode(episode)
    existing_episode = Episode.query.filter_by(title=episode["title"], season_id=season.id).first()
    if existing_episode:
        return existing_episode
    new_episode = Episode(title=episode["title"], number=episode["number"], season=season)
    db.session.add(new_episode)
    return new_episode


def create_movie(movie, playlist):
    validate_movie(movie)
    existing_movie = Movie.query.filter_by(title=movie["title"]).first()
    if existing_movie:
        return existing_movie
    new_movie = Movie(title=movie["title"], year=movie["year"])
    db.session.add(new_movie)
    playlist.movies.append(new_movie)
    return new_movie


def create_photo(photo, playlist):
    validate_photo(photo)
    existing_photo = Photo.query.filter_by(title=photo["title"]).first()
    if existing_photo:
        return existing_photo
    new_photo = Photo(title=photo["title"], file_path=photo["file_path"])
    db.session.add(new_photo)
    playlist.photos.append(new_photo)
    return new_photo


def store_artist_data(playlist_data, new_playlist):
    for artist_name, artist_data in playlist_data.get("artists", {}).items():
        LOGGER.debug(f"Creating artist: {artist_name}")
        new_artist = create_artist({"name": artist_name}, new_playlist)
        for album_name, album_data in artist_data["albums"].items():
            LOGGER.debug(f"Creating album: {album_name}")
            new_album = create_album({"title": album_name}, new_artist)
            for track in album_data["tracks"]:
                LOGGER.debug(f"Creating track: {track['title']}")
                create_track({"title": track["title"], "number": track["number"]}, new_album)


def store_show_data(playlist_data, new_playlist):
    for show_name, show_data in playlist_data.get("shows", {}).items():
        LOGGER.debug(f"Creating show: {show_name}")
        new_show = create_show({"title": show_name}, new_playlist)
        for season_name, season_data in show_data["seasons"].items():
            LOGGER.debug(f"Creating season: {season_name}")
            new_season = create_season({"title": season_name}, new_show)
            for episode in season_data["episodes"]:
                LOGGER.debug(f"Creating episode: {episode['title']}")
                create_episode({"title": episode["title"], "number": episode["number"]}, new_season)


def store_movie_data(playlist_data, new_playlist):
    for movie in playlist_data.get("movies", []):
        LOGGER.debug(f"Creating movie: {movie['title']}")
        create_movie({"title": movie["title"], "year": movie["year"]}, new_playlist)


def store_photo_data(playlist_data, new_playlist):
    for photo in playlist_data.get("photos", []):
        LOGGER.debug(f"Creating photo: {photo['title']}")
        create_photo({"title": photo["title"], "file_path": photo["file_path"]}, new_playlist)


def store_playlist_data():
    LOGGER.info("Storing playlist data...")
    playlist_data = get_playlist_data()

    for playlist_type, playlists in playlist_data.items():
        print(f"Creating category: {playlist_type}")
        new_category = create_playlist_type(playlist_type)
        for playlist_name, playlist in playlists.items():
            LOGGER.debug(f"Creating playlist: {playlist_name}")
            new_playlist = create_playlist({"title": playlist_name}, new_category)
            store_artist_data(playlist, new_playlist)
            store_show_data(playlist, new_playlist)
            store_movie_data(playlist, new_playlist)
            store_photo_data(playlist, new_playlist)

    db.session.commit()
    LOGGER.info("Playlist data stored successfully.")
