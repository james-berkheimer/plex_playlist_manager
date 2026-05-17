"""Service layer: orchestration between the Plex client and domain models."""

from plex_playlist_manager.models import (
    PlaylistSummary,
    PlaylistTree,
    PlexPlaylistSummary,
    PlexTrackItem,
    build_playlist_tree,
)
from plex_playlist_manager.plex_client import PlexClient


async def get_playlist_summaries(client: PlexClient) -> list[PlaylistSummary]:
    """Fetch all editable music playlists and return their summaries.

    Smart playlists are already excluded by the Plex client.

    Args:
        client: The shared PlexClient.

    Returns:
        A list of PlaylistSummary objects, ordered as returned by Plex.
    """
    raw = await client.get_playlists()
    plex_playlists = [PlexPlaylistSummary.model_validate(p) for p in raw]
    return [
        PlaylistSummary(
            rating_key=p.rating_key,
            title=p.title,
            track_count=p.leaf_count,
        )
        for p in plex_playlists
    ]


async def get_playlist_tree(client: PlexClient, playlist_id: str) -> PlaylistTree:
    """Fetch a playlist's items and build an Artist -> Album -> Track tree.

    Args:
        client: The shared PlexClient.
        playlist_id: The Plex playlist ratingKey.

    Returns:
        A PlaylistTree with grouped and sorted artists/albums/tracks.
    """
    raw_summary = await client.get_playlists()
    plex_playlists = [PlexPlaylistSummary.model_validate(p) for p in raw_summary]
    summary = next(p for p in plex_playlists if p.rating_key == playlist_id)

    raw_items = await client.get_playlist_items(playlist_id)
    tracks = [PlexTrackItem.model_validate(item) for item in raw_items]

    return build_playlist_tree(summary.rating_key, summary.title, tracks)
