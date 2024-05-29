from flask import Blueprint, current_app, jsonify, render_template, request
from sqlalchemy import asc

from ...database import db

# from ...models.plex_data_models import Playlist, PlaylistType
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


@playlist_manager_bp.route("/main_2")
def playlist_manager():
    playlist_types = db.session.query(PlaylistType).all()
    playlists_by_type = get_playlist_by_type(playlist_types)

    return render_template(
        "playlist_manager.html", playlist_types=playlist_types, playlists_by_type=playlists_by_type
    )


@index_bp.route("/get_playlist")
def get_playlist():
    playlist_name = request.args.get("name").strip()
    print(f"Playlist name: {playlist_name}")
    playlist = db.session.query(Playlist).filter_by(title=playlist_name).first()
    if playlist is None:
        return jsonify({"error": "Playlist not found"}), 404
    return jsonify(playlist.to_dict())


@index_bp.route("/")
def index():
    plex_service = current_app.config["PLEX_SERVICE"]
    server_name = plex_service.server_name
    return render_template("index.html", server_name=server_name)
