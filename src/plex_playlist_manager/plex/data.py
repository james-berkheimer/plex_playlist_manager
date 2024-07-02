import re


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


def get_sorted_artists(playlist_items):
    artists = {}
    for item in playlist_items:
        if type(item).__name__ == "Track":
            cleaned_name = re.sub(r"\W+", "", item.grandparentTitle).lower()
            artists[cleaned_name] = item.grandparentTitle
    sorted_artists = [artists[artist] for artist in sorted(artists.keys())]
    return sorted_artists


def get_playlist_audio_data(playlists):
    data = {}
    for playlist in playlists:
        playlist_title = playlist.title.strip()
        data[playlist_title] = {}
        sorted_artists = get_sorted_artists(playlist.items())
        for artist_name in sorted_artists:
            if artist_name not in data[playlist_title]:
                data[playlist_title][artist_name] = {}
            for item in playlist.items():
                if type(item).__name__ == "Track" and item.grandparentTitle.strip() == artist_name:
                    album_title = item.parentTitle.strip()
                    if album_title not in data[playlist_title][artist_name]:
                        data[playlist_title][artist_name][album_title] = []
                    track_title = item.title.strip()
                    track_number = item.trackNumber
                    data[playlist_title][artist_name][album_title].append(
                        [track_title, track_number]
                    )
    return data


def get_sorted_titles(playlist_items):
    titles = {}
    for item in playlist_items:
        item_type = type(item).__name__
        if item_type == "Episode":
            cleaned_title = re.sub(r"\W+", "", item.grandparentTitle).lower()
            titles[cleaned_title] = item.grandparentTitle
        elif item_type == "Movie":
            cleaned_title = re.sub(r"\W+", "", item.title).lower()
            titles[cleaned_title] = item.title
    sorted_titles = [titles[title] for title in sorted(titles.keys())]
    return sorted_titles


def get_playlist_video_data(playlists):
    data = {}
    for playlist in playlists:
        playlist_title = playlist.title.strip()
        data[playlist_title] = {}
        sorted_titles = get_sorted_titles(playlist.items())
        for title in sorted_titles:
            for item in playlist.items():
                item_type = type(item).__name__
                if item_type == "Episode" and item.grandparentTitle.strip() == title:
                    if item_type not in data[playlist_title]:
                        data[playlist_title][item_type] = {}

                    if title not in data[playlist_title][item_type]:
                        data[playlist_title][item_type][title] = {}

                    season_title = item.parentTitle.strip()
                    if season_title not in data[playlist_title][item_type][title]:
                        data[playlist_title][item_type][title][season_title] = []

                    episode_title = item.title.strip()
                    episode_number = item.index
                    data[playlist_title][item_type][title][season_title].append(
                        [episode_title, episode_number]
                    )

                if item_type == "Movie" and item.title.strip() == title:
                    movie_year = item.year
                    if item_type not in data[playlist_title]:
                        data[playlist_title][item_type] = {}
                    data[playlist_title][item_type][title] = movie_year

    return data


def get_playlist_photo_data(playlists):
    data = {}
    plex_server_ip = "192.168.1.42"
    plex_server_port = 32400
    for playlist in playlists:
        playlist_title = playlist.title.strip()
        data[playlist_title] = {}

        for item in playlist.items():
            if type(item).__name__ == "Photo":
                photo_title = item.title.strip()
                thumb_url = f"http://{plex_server_ip}:{plex_server_port}{item.thumb}"
                data[playlist_title][photo_title] = thumb_url

    return data


def get_playlist_data(plex_server):
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
        if photo_data:
            playlist_data["photo"] = photo_data

    return playlist_data
