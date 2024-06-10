import re
from pprint import pprint

from flask import current_app


def categorize_playlists(playlists):
    try:
        categorized_playlists = {"audio": [], "video": [], "photo": []}
        for playlist in playlists:
            if playlist.playlistType in categorized_playlists:
                categorized_playlists[playlist.playlistType].append(playlist)
        categorized_playlists = {k: v for k, v in categorized_playlists.items() if v}
        return categorized_playlists
    except Exception as e:
        print(f"Failed to fetch playlists: {e}")
        return None


def get_sorted_artists(playlist):
    sorted_artists = []

    if playlist is not None:
        artists = {}
        for item in playlist.items():
            cleaned_name = re.sub(r"\W+", "", item.grandparentTitle).lower()
            artists[cleaned_name] = item.grandparentTitle
        for artist in sorted(artists.keys()):
            sorted_artists.append(artists[artist])
    return sorted_artists


def get_playlist_audio_data(playlists):
    data = {}
    for playlist in playlists:
        playlist_title = playlist.title.strip()
        data[playlist_title] = {"artists": {}}

        sorted_artists = get_sorted_artists(playlist)
        # print(f"\tPlaylist Title: {playlist_title}")
        # print(f"\tSorted Artists: {sorted_artists}")

        for artist_name in sorted_artists:
            if artist_name not in data[playlist_title]["artists"]:
                data[playlist_title]["artists"][artist_name] = {"albums": {}}

            for item in playlist.items():
                if type(item).__name__ == "Track" and item.grandparentTitle.strip() == artist_name:
                    album_title = item.parentTitle.strip()
                    if album_title not in data[playlist_title]["artists"][artist_name]["albums"]:
                        data[playlist_title]["artists"][artist_name]["albums"][album_title] = {
                            "tracks": []
                        }

                    track_title = item.title.strip()
                    track_number = item.trackNumber
                    data[playlist_title]["artists"][artist_name]["albums"][album_title][
                        "tracks"
                    ].append(
                        {
                            "title": track_title,
                            "number": track_number,
                        }
                    )

    return data


def get_playlist_video_data(playlists):
    data = {}
    for playlist in playlists:
        playlist_title = playlist.title.strip()
        data[playlist_title] = {"shows": {}, "movies": []}

        for item in playlist.items():
            item_type = type(item).__name__
            if item_type == "Episode":
                show_title = item.grandparentTitle.strip()
                if show_title not in data[playlist_title]["shows"]:
                    data[playlist_title]["shows"][show_title] = {"seasons": {}}

                season_title = item.parentTitle.strip()
                if season_title not in data[playlist_title]["shows"][show_title]["seasons"]:
                    data[playlist_title]["shows"][show_title]["seasons"][season_title] = {
                        "episodes": []
                    }

                episode_title = item.title.strip()
                episode_number = item.index
                data[playlist_title]["shows"][show_title]["seasons"][season_title][
                    "episodes"
                ].append(
                    {
                        "title": episode_title,
                        "number": episode_number,
                    }
                )

            if item_type == "Movie":
                movie_title = item.title.strip()
                movie_year = item.year
                data[playlist_title]["movies"].append(
                    {
                        "title": movie_title,
                        "year": movie_year,
                    }
                )

    return data


def get_playlist_photo_data(playlists):
    data = {}
    for playlist in playlists:
        playlist_title = playlist.title.strip()
        data[playlist_title] = {"photos": []}

        for item in playlist.items():
            if type(item).__name__ == "Photo":
                photo_title = item.title.strip()
                photo_path = item.locations[0]
                data[playlist_title]["photos"].append(
                    {
                        "title": photo_title,
                        "path": photo_path,
                    }
                )

    return data


def get_playlist_data():
    plex_service = current_app.config["PLEX_SERVICE"]
    plex_server = plex_service.plex_server
    categorized_playlists = categorize_playlists(plex_server.playlists())
    playlist_data = {}

    if "audio" in categorized_playlists:
        audio_data = get_playlist_audio_data(categorized_playlists["audio"])
        if audio_data:
            playlist_data["audio"] = audio_data

    if "video" in categorized_playlists:
        video_data = get_playlist_video_data(categorized_playlists["video"])
        if video_data:
            playlist_data["video"] = video_data

    if "photo" in categorized_playlists:
        photo_data = get_playlist_photo_data(categorized_playlists["photo"])
        print(photo_data)
        if photo_data:
            playlist_data["photo"] = photo_data

    return playlist_data
