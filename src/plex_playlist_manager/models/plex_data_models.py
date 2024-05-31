from sqlalchemy import and_

from ..database import db

playlist_item_association = db.Table(
    "playlist_item_association",
    db.Column("playlist_id", db.Integer, db.ForeignKey("playlist.id"), primary_key=True),
    db.Column("media_item_id", db.Integer, db.ForeignKey("media_item.id"), primary_key=True),
)


class PlaylistType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    playlists = db.relationship("Playlist", backref="playlist_type", lazy=True)


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    playlist_type_id = db.Column(db.Integer, db.ForeignKey("playlist_type.id"), nullable=False)
    items = db.relationship(
        "MediaItem", secondary=playlist_item_association, backref="playlists", lazy=True
    )

    def to_dict(self):
        playlist_dict = {
            "id": self.id,
            "name": self.name,
            "playlist_type_id": self.playlist_type_id,
            "items": [],
        }

        # Use the appropriate method based on the type of items
        if any(isinstance(item, Track) for item in self.items):
            playlist_dict["items"] = self.get_items_grouped_by_artist_album()
        elif any(isinstance(item, Episode) for item in self.items):
            playlist_dict["items"] = self.get_items_grouped_by_show_season()
        elif any(isinstance(item, Movie) for item in self.items):
            playlist_dict["items"] = self.get_items_grouped_by_movie()
        elif any(isinstance(item, Photo) for item in self.items):
            playlist_dict["items"] = self.get_items_grouped_by_photo()
        else:
            playlist_dict["items"] = [item.title for item in self.items]

        return playlist_dict

    def get_items_grouped_by_artist_album(self):
        grouped_items = {}
        for item in self.items:
            if isinstance(item, Track):
                artist_name = item.artist.name
                album_title = item.album.title
                if artist_name not in grouped_items:
                    grouped_items[artist_name] = {}
                if album_title not in grouped_items[artist_name]:
                    grouped_items[artist_name][album_title] = []
                grouped_items[artist_name][album_title].append(item.title)
        return grouped_items

    def get_items_grouped_by_show_season(self):
        grouped = {}
        for item in self.items:
            if isinstance(item, Episode):
                show_title = item.show.title
                season_title = item.season.title
                episode_title = item.title
                print(f"Show: {show_title}, \nSeason: {season_title}, \nEpisode: {episode_title}")

                if show_title not in grouped:
                    grouped[show_title] = {}
                if season_title not in grouped[show_title]:
                    grouped[show_title][season_title] = []
                grouped[show_title][season_title].append(episode_title)
        return grouped

    def get_items_grouped_by_movie(self):
        grouped = {}
        for item in self.items:
            if isinstance(item, Movie):
                release_year = item.year
                if release_year not in grouped:
                    grouped[release_year] = []
                grouped[release_year].append(item.title)
        return grouped

    def get_items_grouped_by_photo(self):
        grouped = {}
        for item in self.items:
            if isinstance(item, Photo):
                photo_title = item.title
                if photo_title not in grouped:
                    grouped[photo_title] = []
                grouped[photo_title].append(item.file_path)
        return grouped


class MediaItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "media_item"}


class Artist(MediaItem):
    id = db.Column(db.Integer, db.ForeignKey("media_item.id"), primary_key=True)
    name = db.Column(db.String, nullable=False)

    albums = db.relationship(
        "Album", back_populates="artist", lazy=True, foreign_keys="Album.artist_id"
    )
    tracks = db.relationship(
        "Track", back_populates="artist", lazy=True, foreign_keys="Track.artist_id"
    )

    __mapper_args__ = {"polymorphic_identity": "artist"}


class Album(MediaItem):
    id = db.Column(db.Integer, db.ForeignKey("media_item.id"), primary_key=True)
    title = db.Column(db.String, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)

    artist = db.relationship("Artist", back_populates="albums", foreign_keys="Album.artist_id")
    tracks = db.relationship(
        "Track", back_populates="album", lazy=True, foreign_keys="Track.album_id"
    )

    __mapper_args__ = {"polymorphic_identity": "album"}


class Track(MediaItem):
    id = db.Column(db.Integer, db.ForeignKey("media_item.id"), primary_key=True)
    title = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey("album.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)

    album = db.relationship("Album", back_populates="tracks", foreign_keys="Track.album_id")
    artist = db.relationship("Artist", back_populates="tracks", foreign_keys="Track.artist_id")

    __mapper_args__ = {"polymorphic_identity": "track", "properties": {"number": number}}


class Show(MediaItem):
    id = db.Column(db.Integer, db.ForeignKey("media_item.id"), primary_key=True)
    title = db.Column(db.String, nullable=False)

    seasons = db.relationship(
        "Season", back_populates="show", lazy=True, foreign_keys="Season.show_id"
    )
    episodes = db.relationship(
        "Episode", back_populates="show", lazy=True, foreign_keys="Episode.show_id"
    )

    __mapper_args__ = {"polymorphic_identity": "show"}


class Season(MediaItem):
    id = db.Column(db.Integer, db.ForeignKey("media_item.id"), primary_key=True)
    title = db.Column(db.String, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"), nullable=False)

    show = db.relationship("Show", back_populates="seasons", foreign_keys="Season.show_id")
    episodes = db.relationship(
        "Episode", back_populates="season", lazy=True, foreign_keys="Episode.season_id"
    )

    __mapper_args__ = {"polymorphic_identity": "season"}


class Episode(MediaItem):
    id = db.Column(db.Integer, db.ForeignKey("media_item.id"), primary_key=True)
    title = db.Column(db.String, nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey("season.id"), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey("show.id"), nullable=False)

    season = db.relationship("Season", back_populates="episodes", foreign_keys="Episode.season_id")
    show = db.relationship("Show", back_populates="episodes", foreign_keys="Episode.show_id")

    __mapper_args__ = {"polymorphic_identity": "episode"}


class Movie(MediaItem):
    id = db.Column(db.Integer, db.ForeignKey("media_item.id"), primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {"polymorphic_identity": "movie"}


class Photo(MediaItem):
    id = db.Column(db.Integer, db.ForeignKey("media_item.id"), primary_key=True)
    title = db.Column(db.String, nullable=False)
    file_path = db.Column(db.String(500), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "photo"}
