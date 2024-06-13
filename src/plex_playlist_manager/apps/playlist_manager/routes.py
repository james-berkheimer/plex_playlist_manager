import json

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
        playlist_types = redis_client.keys("*")
        for playlist_type in playlist_types:
            encoded_data = redis_client.hgetall(playlist_type)
            decoded_playlists_names = []
            for key, _value in encoded_data.items():
                decoded_playlists_names.append(key.decode())
            categorized_playlists[playlist_type.decode()] = decoded_playlists_names
        return categorized_playlists
    except Exception as e:
        print(f"Failed to fetch playlists: {e}")
        return None


@playlist_manager_bp.route("/")
def playlist_manager():
    redis_client = get_db()
    return render_template(
        "playlist_manager.html", categorized_playlists=categorize_playlists(redis_client)
    )


@get_playlist_items_bp.route("/get_playlist_items", methods=["POST"])
def get_playlist_items():
    playlist_type = request.form.get("playlist_type").strip()
    playlist_title = request.form.get("playlist_title").strip()
    print(f"Playlist type: {playlist_type}, Playlist title: {playlist_title}")

    redis_client = get_db()
    playlist_data_bytes = redis_client.hget(playlist_type, playlist_title)

    if playlist_data_bytes is None:
        return jsonify({"error": "Playlist not found"}), 404

    playlist_data_str = playlist_data_bytes.decode("utf-8")
    playlist_data = json.loads(playlist_data_str)

    return jsonify(playlist_data)


# Populate Redis cache when server starts
make_db(redis_db, plex_data)
