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

    async def get_playlists(self) -> dict[str, Any]:
        """Return the raw MediaContainer for all playlists on the server."""
        return await self._get("/playlists")

    async def get_playlist_items(self, playlist_id: int | str) -> dict[str, Any]:
        """Return the raw MediaContainer for all items in a playlist."""
        return await self._get(f"/playlists/{playlist_id}/items")
