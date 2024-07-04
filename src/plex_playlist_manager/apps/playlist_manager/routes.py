import json
from pprint import pprint

from flask import Blueprint, jsonify, render_template, request
from redis import StrictRedis

from ...cache.redis import get_db, make_db
from ...config import plex_server
from ...plex.data import get_playlist_data

plex_data = get_playlist_data(plex_server)

redis_db = StrictRedis(host="localhost", port=6379, db=0)

get_playlist_items_bp = Blueprint("get_playlist_items", __name__)
playlist_manager_bp = Blueprint("playlist_manager", __name__)


def categorize_playlists(redis_client):
    try:
        categorized_playlists = {}
        # Decode and sort playlist types
        playlist_types = sorted([pt.decode() for pt in redis_client.keys("*")])
        for playlist_type in playlist_types:
            encoded_data = redis_client.hgetall(playlist_type.encode())
            # Decode and sort playlist names
            decoded_playlists_names = sorted([key.decode() for key in encoded_data.keys()])
            categorized_playlists[playlist_type] = decoded_playlists_names
        return categorized_playlists
    except Exception as e:
        print(f"Failed to fetch playlists: {e}")
        return None


@playlist_manager_bp.route("/")
def playlist_manager():
    redis_client = get_db()
    return render_template(
        "playlist_manager/playlist_manager_main.html",
        categorized_playlists=categorize_playlists(redis_client),
    )


@get_playlist_items_bp.route("/get_playlist_items", methods=["POST"])
def get_playlist_items():
    # Access request.json once
    request_data = request.json
    print(f"request: {request_data}")  # Debugging print

    # Error handling for missing or blank fields
    playlist_type = request_data.get("playlist_type", "").strip()
    playlist_title = request_data.get("playlist_title", "").strip()
    if not playlist_type or not playlist_title:
        return jsonify({"error": "Missing or blank playlist type or title"}), 400

    print(f"Playlist type: {playlist_type}, Playlist title: {playlist_title}")

    redis_client = get_db()
    playlist_data_bytes = redis_client.hget(playlist_type, playlist_title)

    if playlist_data_bytes is None:
        return jsonify({"error": "Playlist not found"}), 404

    playlist_data_str = playlist_data_bytes.decode("utf-8")
    playlist_data = json.loads(playlist_data_str)

    # Mapping of playlist types to templates
    templates = {
        "audio": "playlist_manager/audio_playlist.html",
        "video": "playlist_manager/video_playlist.html",
        "photo": "playlist_manager/photo_playlist.html",
    }

    template = templates.get(playlist_type)
    if template:
        # Check if playlist type is audio or video to include enumerate
        if playlist_type in ["audio", "video"]:
            return render_template(template, data_dict=playlist_data, enumerate=enumerate)
        else:
            return render_template(template, data_dict=playlist_data)
    else:
        return jsonify({"error": "Invalid playlist type"}), 400


# Populate Redis cache when server starts
make_db(redis_db, plex_data)
