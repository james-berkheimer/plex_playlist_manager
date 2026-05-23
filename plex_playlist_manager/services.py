"""Service layer: orchestration between the Plex client and domain models."""

import logging
from dataclasses import dataclass, field

import httpx

from plex_playlist_manager.models import (
    PlaylistSummary,
    PlaylistTree,
    PlexPlaylistSummary,
    PlexTrackItem,
    build_playlist_tree,
)
from plex_playlist_manager.plex_client import PlexClient

logger = logging.getLogger(__name__)


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


@dataclass
class DeletionResult:
    """Outcome of a batch deletion call.

    Attributes:
        succeeded: playlist_item_id values that were deleted successfully.
        failed: list of (playlist_item_id, error_message) for items that
            could not be deleted.
    """

    succeeded: list[int] = field(default_factory=list)
    failed: list[tuple[int, str]] = field(default_factory=list)

    @property
    def total_attempted(self) -> int:
        return len(self.succeeded) + len(self.failed)


async def delete_playlist_items(
    client: PlexClient,
    playlist_id: str,
    playlist_item_ids: list[int],
) -> DeletionResult:
    """Delete multiple items from a playlist, one request at a time.

    Deletes run sequentially. If a single deletion fails, the error is
    recorded and the loop continues with the remaining items.

    Args:
        client: The shared PlexClient.
        playlist_id: The Plex playlist ratingKey.
        playlist_item_ids: The playlistItemID values to remove.

    Returns:
        A DeletionResult summarizing which deletions succeeded and which
        failed (with their error messages).
    """
    result = DeletionResult()

    for item_id in playlist_item_ids:
        try:
            await client.delete_playlist_item(playlist_id, item_id)
            result.succeeded.append(item_id)
        except httpx.HTTPError as exc:
            message = f"{type(exc).__name__}: {exc}"
            logger.warning(
                f"Failed to delete playlistItemID={item_id} from playlist {playlist_id}: {message}"
            )
            result.failed.append((item_id, message))

    return result
