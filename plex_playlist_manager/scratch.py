"""Scratch file for ad-hoc Plex API experiments.

Run with:
    python -m plex_playlist_manager.scratch
"""

import asyncio

from plex_playlist_manager.config import get_settings
from plex_playlist_manager.plex_client import PlexClient


async def main() -> None:
    import json

    client = PlexClient(get_settings())
    try:
        data = await client.get_playlists()
        playlists = data["MediaContainer"].get("Metadata", [])

        target = next(p for p in playlists if p.get("title") == "Optima Cantica")
        playlist_id = target["ratingKey"]
        print(f"Inspecting playlist: {target['title']} (id={playlist_id})")
        print(f"smart={target.get('smart')}, leafCount={target.get('leafCount')}")

        items_data = await client.get_playlist_items(playlist_id)
        container = items_data["MediaContainer"]
        print("\nMediaContainer top-level keys and values:")
        for key, value in container.items():
            if key != "Metadata":
                print(f"  {key}: {value!r}")

        items = container.get("Metadata", [])
        print(f"\nReturned items count: {len(items)}")

        if items:
            print("\nFirst item full JSON:")
            print(json.dumps(items[0], indent=2))
    finally:
        await client.close()


def run() -> None:
    """Console script entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
