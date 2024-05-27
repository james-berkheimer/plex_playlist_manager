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


def get_playlist_audio_data(playlists):
    data = {}
    for playlist in playlists:
        playlist_title = playlist.title.strip()
        data[playlist_title] = {"artists": {}}

        for item in playlist.items():
            if type(item).__name__ == "Track":
                artist_name = item.grandparentTitle.strip()
                if artist_name not in data[playlist_title]["artists"]:
                    data[playlist_title]["artists"][artist_name] = {"albums": {}}

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


def get_playlist_data():
    plex_service = current_app.config["PLEX_SERVICE"]
    plex_server = plex_service.plex_server
    categorized_playlists = categorize_playlists(plex_server.playlists())
    playlist_data = {
        "audio": get_playlist_audio_data(categorized_playlists["audio"]),
        "video": get_playlist_video_data(categorized_playlists["video"]),
    }
    return playlist_data
