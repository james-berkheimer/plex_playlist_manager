from flask import redirect, render_template, request, url_for

from ..config import LOGGER, PLEX
from .app import app

# playlists = PLEX.playlists()


def get_playlists(playlists):
    LOGGER.info("Fetching playlists")
    try:
        categorized_playlists = {"audio": [], "video": [], "photo": []}
        for playlist in playlists:
            if playlist.playlistType in categorized_playlists:
                categorized_playlists[playlist.playlistType].append(playlist)
        # Remove empty playlist groups
        categorized_playlists = {k: v for k, v in categorized_playlists.items() if v}
        return categorized_playlists
    except Exception as e:
        print(f"Failed to fetch playlists: {e}")
        return {}


def get_playlist_audio_data(playlists):
    LOGGER.info("Fetching playlist data")
    all_playlist_data = {}
    for playlist in playlists["audio"]:
        print(f"playlist: {playlist.title}")
        playlist_title = playlist.title.strip()
        playlist_data = {playlist_title: {}}

        for item in playlist.items():
            artist = item.grandparentTitle.strip()
            album = item.parentTitle.strip()
            track = item.title.strip()
            track_number = item.trackNumber

            artist_albums = playlist_data[playlist_title].setdefault(artist, {})
            album_tracks = artist_albums.setdefault(album, [])
            album_tracks.append((track_number, track))

        all_playlist_data.update(playlist_data)  # Add this playlist's data to the main dictionary

    return all_playlist_data


@app.route("/gui")
def gui():
    return render_template("gui.html")


@app.route("/base")
def base():
    return render_template("base.html")


@app.route("/main_2")
def main_2():
    playlists = PLEX.playlists()
    categorized_playlists = get_playlists(playlists)
    return render_template("main_2.html", playlists=categorized_playlists)


@app.route("/")
def index():
    playlists = PLEX.playlists()
    categorized_playlists = get_playlists(playlists)
    audio_data = get_playlist_audio_data(categorized_playlists)
    server_name = PLEX.friendlyName
    return render_template("index.html", audio_data=audio_data, server_name=server_name)
