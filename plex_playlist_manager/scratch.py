"""Scratch file for ad-hoc Plex API experiments.

Run with:
    python -m plex_playlist_manager.scratch
"""

import asyncio

from plex_playlist_manager.config import get_settings
from plex_playlist_manager.plex_client import PlexClient


async def main() -> None:
    from plex_playlist_manager.models import (
        PlexPlaylistSummary,
        PlexTrackItem,
        build_playlist_tree,
    )

    client = PlexClient(get_settings())
    try:
        raw_playlists = await client.get_playlists()
        playlists = [PlexPlaylistSummary.model_validate(p) for p in raw_playlists]
        target = next(p for p in playlists if p.title == "Optima Cantica")

        raw_items = await client.get_playlist_items(target.rating_key)
        tracks = [PlexTrackItem.model_validate(item) for item in raw_items]
        tree = build_playlist_tree(target.rating_key, target.title, tracks)

        print(f"Letters present: {tree.letters_present}\n")

        print("Bucket assignments (first 5 per letter):")
        from collections import defaultdict

        by_letter: dict[str, list[str]] = defaultdict(list)
        for artist in tree.artists:
            by_letter[artist.bucket_letter].append(artist.name)

        for letter in tree.letters_present:
            names = by_letter[letter]
            sample = ", ".join(names[:5])
            print(f"  {letter}: ({len(names)}) {sample}")
    finally:
        await client.close()


def run() -> None:
    """Console script entry point."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
