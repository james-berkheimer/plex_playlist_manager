import re

from ..config import plex_server


def categorized_playlists():
    playlists = plex_server.playlists()
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


def _get_sorted_artists(playlist_items):
    artists = {}
    for item in playlist_items:
        if type(item).__name__ == "Track":
            cleaned_name = re.sub(r"\W+", "", item.grandparentTitle).lower()
            artists[cleaned_name] = item.grandparentTitle
    sorted_artists = [artists[artist] for artist in sorted(artists.keys())]
    return sorted_artists


def _playlist_audio_data(playlist_title):
    data = {}
    playlist = plex_server.playlist(playlist_title)
    sorted_artists = _get_sorted_artists(playlist.items())
    for artist_name in sorted_artists:
        if artist_name not in data:
            data[artist_name] = {}
        for item in playlist.items():
            if type(item).__name__ == "Track" and item.grandparentTitle.strip() == artist_name:
                album_title = item.parentTitle.strip()
                if album_title not in data[artist_name]:
                    data[artist_name][album_title] = []
                track_title = item.title.strip()
                track_number = item.trackNumber
                data[artist_name][album_title].append([track_title, track_number])
    return data


def _playlist_audio_details(playlist_title):
    details_dict = {}
    playlist = plex_server.playlist(playlist_title)
    details_dict["title"] = playlist.title
    details_dict["total_items"] = len(playlist.items())

    days = playlist.duration // (24 * 3600 * 1000)
    hours = (playlist.duration % (24 * 3600 * 1000)) // (3600 * 1000)
    minutes = (playlist.duration % (3600 * 1000)) // 60000
    seconds = (playlist.duration % 60000) // 1000
    details_dict["duration"] = f"{days}:{hours}:{minutes}:{seconds}"

    return details_dict


def _playlist_photo_details(playlist_title):
    pass


def _playlist_video_details(playlist_title):
    pass


def _get_sorted_titles(playlist_items):
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


def _playlist_video_data(playlist_title):
    data = {"Episode": {}, "Movie": {}}
    playlist = plex_server.playlist(playlist_title)
    sorted_titles = _get_sorted_titles(playlist.items())
    for title in sorted_titles:
        for item in playlist.items():
            item_type = type(item).__name__
            if item_type == "Episode" and item.grandparentTitle.strip() == title:
                if title not in data[item_type]:
                    data[item_type][title] = {}

                season_title = item.parentTitle.strip()
                if season_title not in data[item_type][title]:
                    data[item_type][title][season_title] = []

                episode_title = item.title.strip()
                episode_number = item.index
                data[item_type][title][season_title].append([episode_title, episode_number])

            elif item_type == "Movie" and item.title.strip() == title:
                movie_year = item.year
                data[item_type][title] = movie_year

    return data


def _playlist_photo_data(playlist_title):
    data = {}
    plex_server_ip = "192.168.1.42"
    plex_server_port = 32400
    playlist = plex_server.playlist(playlist_title)

    for item in playlist.items():
        if type(item).__name__ == "Photo":
            photo_title = item.title.strip()
            thumb_url = f"http://{plex_server_ip}:{plex_server_port}{item.thumb}"
            data[photo_title] = thumb_url

    return data


def playlist_data(playlist_type, playlist_title):
    if playlist_type == "audio":
        return _playlist_audio_data(playlist_title)
    if playlist_type == "video":
        return _playlist_video_data(playlist_title)
    if playlist_type == "photo":
        return _playlist_photo_data(playlist_title)
    return None


def playlist_details(playlist_type, playlist_title):
    if playlist_type == "audio":
        return _playlist_audio_details(playlist_title)
    if playlist_type == "video":
        return _playlist_video_details(playlist_title)
    if playlist_type == "photo":
        return _playlist_photo_details(playlist_title)
    return None
