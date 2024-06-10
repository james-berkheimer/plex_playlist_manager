import time

from flask import Blueprint, current_app, jsonify, render_template, request
from sqlalchemy import asc

from ...database import db
from ...models.plex_data_models import Playlist, PlaylistType

index_bp = Blueprint("index", __name__)
playlist_manager_bp = Blueprint("playlist_manager", __name__)


def get_playlist_by_type(playlist_types):
    playlists_by_type = {}
    for playlist_type in playlist_types:
        playlists_by_type[playlist_type.name] = (
            db.session.query(Playlist).filter_by(playlist_type_id=playlist_type.id).all()
        )
    return playlists_by_type


@playlist_manager_bp.route("/")
def playlist_manager():
    playlist_types = db.session.query(PlaylistType).all()
    playlists_by_type = get_playlist_by_type(playlist_types)

    return render_template(
        "playlist_manager.html", playlist_types=playlist_types, playlists_by_type=playlists_by_type
    )


@index_bp.route("/get_playlist")
def get_playlist():
    start_time = time.time()

    playlist_name = request.args.get("name").strip()
    playlist = db.session.query(Playlist).filter_by(name=playlist_name).first()
    if playlist is None:
        return jsonify({"error": "Playlist not found"}), 404
    playlist_data = playlist.to_dict()
    playlist_data["items"] = list(playlist_data["items"].items())  # Convert dict to list of tuples

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time} seconds")

    return jsonify(playlist_data)
