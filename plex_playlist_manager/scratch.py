"""Scratch file for ad-hoc Plex API experiments.

Run with:
    python -m plex_playlist_manager.scratch
"""

import asyncio

from plex_playlist_manager.config import get_settings
from plex_playlist_manager.plex_client import PlexClient


async def main() -> None:
    from plex_playlist_manager.models import PlexPlaylistSummary, PlexTrackItem
    from plex_playlist_manager.services import delete_playlist_items

    client = PlexClient(get_settings())
    try:
        raw_playlists = await client.get_playlists()
        playlists = [PlexPlaylistSummary.model_validate(p) for p in raw_playlists]
        target = next(p for p in playlists if p.title == "Test_01")

        raw_items_before = await client.get_playlist_items(target.rating_key)
        tracks_before = [PlexTrackItem.model_validate(item) for item in raw_items_before]
        print(f"Before: {len(tracks_before)} tracks in '{target.title}'")

        victims = [t for t in tracks_before[-2:] if t.playlist_item_id is not None]
        if len(victims) < 2:
            print("ERROR: need at least 2 deletable tracks at end of playlist.")
            return

        bogus_id = 999999999
        ids_to_delete = [victims[0].playlist_item_id, bogus_id, victims[1].playlist_item_id]

        print(f"Deleting playlistItemIDs: {ids_to_delete}")
        print(f"  (middle ID {bogus_id} is bogus and should fail)")

        result = await delete_playlist_items(client, target.rating_key, ids_to_delete)

        print(f"\nResult:")
        print(f"  total_attempted: {result.total_attempted}")
        print(f"  succeeded ({len(result.succeeded)}): {result.succeeded}")
        print(f"  failed ({len(result.failed)}):")
        for item_id, message in result.failed:
            print(f"    {item_id}: {message}")

        raw_items_after = await client.get_playlist_items(target.rating_key)
        tracks_after = [PlexTrackItem.model_validate(item) for item in raw_items_after]
        print(f"\nAfter: {len(tracks_after)} tracks in '{target.title}'")

        delta = len(tracks_before) - len(tracks_after)
        print(f"Delta: {delta} (expected 2)")

        remaining_ids = {t.playlist_item_id for t in tracks_after}
        for victim in victims:
            still_present = victim.playlist_item_id in remaining_ids
            print(
                f"  playlistItemID={victim.playlist_item_id} still present: "
                f"{still_present} (expected False)"
            )
    finally:
        await client.close()


def run() -> None:
    """Console script entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
