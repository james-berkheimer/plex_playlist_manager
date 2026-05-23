from typing import Any

import httpx

from plex_playlist_manager.config import Settings


class PlexClient:
    """Async HTTP client for the Plex Media Server API."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = str(settings.plex_base_url).rstrip("/")
        self._headers = {
            "X-Plex-Token": settings.plex_token,
            "Accept": "application/json",
        }
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=30.0,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def _get(self, path: str) -> dict[str, Any]:
        """Perform an authenticated GET request and return the parsed JSON body."""
        response = await self._client.get(path)
        response.raise_for_status()
        return response.json()

    async def get_playlists(self) -> list[dict[str, Any]]:
        """Return non-smart music playlists from the server.

        Smart playlists are excluded because they cannot be edited via the API.

        Returns:
            A list of playlist Metadata dicts.
        """
        response = await self._client.get(
            "/playlists",
            params={"playlistType": "audio"},
        )
        response.raise_for_status()
        container = response.json()["MediaContainer"]
        playlists = container.get("Metadata", [])
        return [p for p in playlists if not p.get("smart")]

    async def get_playlist_items(
        self,
        playlist_id: int | str,
        page_size: int = 500,
    ) -> list[dict[str, Any]]:
        """Return all items in a playlist, transparently handling pagination.

        Args:
            playlist_id: The Plex playlist ratingKey.
            page_size: Number of items to request per page.

        Returns:
            A flat list of item dicts (Plex Metadata entries).
        """
        items: list[dict[str, Any]] = []
        start = 0

        while True:
            params = {
                "X-Plex-Container-Start": start,
                "X-Plex-Container-Size": page_size,
            }
            response = await self._client.get(
                f"/playlists/{playlist_id}/items",
                params=params,
            )
            response.raise_for_status()
            container = response.json()["MediaContainer"]

            page_items = container.get("Metadata", [])
            items.extend(page_items)

            total_size = container.get("totalSize", container.get("size", len(items)))
            if len(items) >= total_size or not page_items:
                break

            start += page_size

        return items

    async def delete_playlist_item(
        self,
        playlist_id: int | str,
        playlist_item_id: int | str,
    ) -> None:
        """Remove a single item from a playlist.

        Wraps DELETE /playlists/{playlist_id}/items/{playlist_item_id}.
        Raises httpx.HTTPStatusError if Plex returns a non-2xx response.

        Args:
            playlist_id: The Plex playlist ratingKey.
            playlist_item_id: The per-playlist item identifier (playlistItemID).
                This is NOT the track's ratingKey.
        """
        response = await self._client.delete(
            f"/playlists/{playlist_id}/items/{playlist_item_id}",
        )
        response.raise_for_status()
