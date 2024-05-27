from ..database import db

playlist_artists = db.Table(
    "playlist_artists",
    db.Column("playlist_id", db.Integer, db.ForeignKey("playlist.id"), primary_key=True),
    db.Column("artist_id", db.Integer, db.ForeignKey("artist.id"), primary_key=True),
)

playlist_shows = db.Table(
    "playlist_shows",
    db.Column("playlist_id", db.Integer, db.ForeignKey("playlist.id"), primary_key=True),
    db.Column("show_id", db.Integer, db.ForeignKey("show.id"), primary_key=True),
)

playlist_movies = db.Table(
    "playlist_movies",
    db.Column("playlist_id", db.Integer, db.ForeignKey("playlist.id"), primary_key=True),
    db.Column("movie_id", db.Integer, db.ForeignKey("movie.id"), primary_key=True),
)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(120), nullable=False)
    artists = db.relationship(
        "Artist",
        secondary=playlist_artists,
        lazy="subquery",
        backref=db.backref("playlists", lazy=True),
    )
    movies = db.relationship(
        "Movie",
        secondary=playlist_movies,
        lazy="subquery",
        backref=db.backref("playlists", lazy=True),
    )
    shows = db.relationship(
        "Show",
        secondary=playlist_shows,
        lazy="subquery",
        backref=db.backref("playlists", lazy=True),
    )


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    year = db.Column(db.Integer)


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    seasons = db.relationship("Season", backref="show", lazy=True)


class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"), nullable=False)
    episodes = db.relationship("Episode", backref="season", lazy=True)


class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    number = db.Column(db.Integer)
    season_id = db.Column(db.Integer, db.ForeignKey("season.id"), nullable=False)


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    albums = db.relationship("Album", backref="artist", lazy=True)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    tracks = db.relationship("Track", backref="album", lazy=True)


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    number = db.Column(db.Integer)
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), nullable=False)
