from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///plex_playlist_manager.db"
db = SQLAlchemy(app)


# Define your models
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, default=0)
    tracks = db.relationship("Track", secondary="playlist_tracks", back_populates="playlists")


class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, default=0)
    albums = db.relationship("Album", back_populates="artist")
    tracks = db.relationship("Track", back_populates="artist")


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, default=0)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    artist = db.relationship("Artist", back_populates="albums")
    tracks = db.relationship("Track", back_populates="album")


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    album = db.relationship("Album", back_populates="tracks")
    artist = db.relationship("Artist", back_populates="tracks")
    playlists = db.relationship("Playlist", secondary="playlist_tracks", back_populates="tracks")


# Association table
playlist_tracks = db.Table(
    "playlist_tracks",
    db.Column("playlist_id", db.Integer, db.ForeignKey("playlist.id"), primary_key=True),
    db.Column("track_id", db.Integer, db.ForeignKey("track.id"), primary_key=True),
)

# Create tables
with app.app_context():
    db.create_all()


# Example route
@app.route("/")
def index():
    new_playlist = Playlist(name="New Playlist")
    db.session.add(new_playlist)
    db.session.commit()
    return "Playlist added!"


if __name__ == "__main__":
    app.run(debug=True)
