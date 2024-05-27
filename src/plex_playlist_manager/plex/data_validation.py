def validate_playlist(playlist):
    assert "title" in playlist, "Missing 'title' in playlist"


def validate_playlist_type(playlist_type_name):
    assert isinstance(playlist_type_name, str), "Playlist type name must be a string"
    assert playlist_type_name, "Playlist type name must not be empty"


def validate_artist(artist):
    assert "name" in artist, "Missing 'name' in artist"


def validate_album(album):
    assert "title" in album, "Missing 'title' in album"


def validate_track(track):
    assert "title" in track, "Missing 'title' in track"
    assert "number" in track, "Missing 'number' in track"


def validate_show(show):
    assert "title" in show, "Missing 'title' in show"


def validate_season(season):
    assert "title" in season, "Missing 'title' in season"


def validate_episode(episode):
    assert "title" in episode, "Missing 'title' in episode"
    assert "number" in episode, "Missing 'number' in episode"


def validate_movie(movie):
    assert "title" in movie, "Missing 'title' in movie"
    assert "year" in movie, "Missing 'year' in movie"


def validate_photo(photo):
    assert "title" in photo, "Missing 'title' in photo"
    assert "file_path" in photo, "Missing 'file_path' in photo"
