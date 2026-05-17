"""Pydantic models for Plex API ingestion and the application's domain layer."""

import unicodedata

from pydantic import BaseModel, ConfigDict, Field

_LEADING_ARTICLES = ("the ", "a ", "an ")


def _bucket_letter(name: str) -> str:
    """Determine the alphabetical bucket for an artist name.

    Leading articles ('the', 'a', 'an') are stripped. Accented characters
    are normalized to their base letter. Non-alphabetic first characters
    bucket to '#'.

    Args:
        name: The artist's display name.

    Returns:
        A single uppercase letter A-Z, or '#' for numeric/symbolic names.
    """
    stripped = name.strip().casefold()
    for article in _LEADING_ARTICLES:
        if stripped.startswith(article):
            stripped = stripped[len(article) :]
            break

    if not stripped:
        return "#"

    normalized = unicodedata.normalize("NFKD", stripped)
    first = next((c for c in normalized if not unicodedata.combining(c)), "")

    if first.isalpha():
        return first.upper()
    return "#"


class _PlexBase(BaseModel):
    """Base for Plex API models.

    Plex returns many more fields than we use. `extra='ignore'` lets us
    define only what we care about without breaking on unknown fields.
    """

    model_config = ConfigDict(extra="ignore")


class PlexPlaylistSummary(_PlexBase):
    """A single playlist entry from `GET /playlists`."""

    rating_key: str = Field(alias="ratingKey")
    title: str
    playlist_type: str = Field(alias="playlistType")
    smart: bool
    leaf_count: int = Field(alias="leafCount")
    duration: int = 0
    composite: str | None = None


class PlexTrackItem(_PlexBase):
    """A single track from `GET /playlists/{id}/items`."""

    rating_key: str = Field(alias="ratingKey")
    playlist_item_id: int | None = Field(default=None, alias="playlistItemID")
    title: str
    parent_title: str = Field(alias="parentTitle")
    grandparent_title: str = Field(alias="grandparentTitle")
    parent_year: int | None = Field(default=None, alias="parentYear")
    index: int | None = None
    parent_index: int | None = Field(default=None, alias="parentIndex")
    duration: int = 0


class Track(BaseModel):
    """A single track in a playlist tree."""

    rating_key: str
    playlist_item_id: int | None
    title: str
    track_number: int | None
    disc_number: int | None
    duration_ms: int


class Album(BaseModel):
    """An album node in a playlist tree, containing its tracks."""

    title: str
    year: int | None
    tracks: list[Track]

    @property
    def duration_ms(self) -> int:
        """Total duration of this album's tracks in milliseconds."""
        return sum(t.duration_ms for t in self.tracks)


class Artist(BaseModel):
    """An artist node in a playlist tree, containing their albums."""

    name: str
    bucket_letter: str
    albums: list[Album]

    @property
    def track_count(self) -> int:
        """Total number of tracks across all this artist's albums."""
        return sum(len(a.tracks) for a in self.albums)

    @property
    def duration_ms(self) -> int:
        """Total duration of this artist's tracks in milliseconds."""
        return sum(a.duration_ms for a in self.albums)


class PlaylistSummary(BaseModel):
    """A slim playlist representation for the playlist list view."""

    rating_key: str
    title: str
    track_count: int


class PlaylistTree(BaseModel):
    """A playlist rendered as an Artist -> Album -> Track tree."""

    rating_key: str
    title: str
    artists: list[Artist]
    letters_present: list[str]

    @property
    def track_count(self) -> int:
        """Total number of tracks across all artists."""
        return sum(a.track_count for a in self.artists)

    @property
    def duration_ms(self) -> int:
        """Total duration of all tracks in this playlist in milliseconds."""
        return sum(a.duration_ms for a in self.artists)


def build_playlist_tree(
    rating_key: str,
    title: str,
    items: list[PlexTrackItem],
) -> PlaylistTree:
    """Build an Artist -> Album -> Track tree from a flat list of Plex items.

    Tracks within an album are sorted by (disc_number, track_number).
    Albums within an artist are sorted by (year, title).
    Artists are sorted alphabetically, case-insensitive.

    Args:
        rating_key: The Plex playlist ratingKey.
        title: The playlist's display title.
        items: Flat list of tracks as returned by the Plex API.

    Returns:
        A PlaylistTree with grouped and sorted artists/albums/tracks.
    """
    # Nested dict accumulator: artist_name -> album_key -> list[Track]
    # album_key is (album_title, year) to disambiguate same-titled albums
    # from different years.
    grouped: dict[str, dict[tuple[str, int | None], list[Track]]] = {}

    # Track album year per (artist, album_key) since the key includes it
    # and we need it back when constructing Album objects.
    for item in items:
        artist_name = item.grandparent_title or "Unknown Artist"
        album_title = item.parent_title or "Unknown Album"
        album_key = (album_title, item.parent_year)

        track = Track(
            rating_key=item.rating_key,
            playlist_item_id=item.playlist_item_id,
            title=item.title,
            track_number=item.index,
            disc_number=item.parent_index,
            duration_ms=item.duration,
        )

        grouped.setdefault(artist_name, {}).setdefault(album_key, []).append(track)

    artists: list[Artist] = []
    for artist_name in sorted(grouped, key=str.casefold):
        albums_dict = grouped[artist_name]
        albums: list[Album] = []
        for (album_title, year), tracks in albums_dict.items():
            tracks_sorted = sorted(
                tracks,
                key=lambda t: (
                    t.disc_number if t.disc_number is not None else 1,
                    t.track_number if t.track_number is not None else 10**9,
                ),
            )
            albums.append(Album(title=album_title, year=year, tracks=tracks_sorted))

        albums.sort(
            key=lambda a: (
                a.year if a.year is not None else 10**9,
                a.title.casefold(),
            )
        )
        artists.append(
            Artist(
                name=artist_name,
                bucket_letter=_bucket_letter(artist_name),
                albums=albums,
            )
        )

    letters_present = sorted({a.bucket_letter for a in artists})

    return PlaylistTree(
        rating_key=rating_key,
        title=title,
        artists=artists,
        letters_present=letters_present,
    )
