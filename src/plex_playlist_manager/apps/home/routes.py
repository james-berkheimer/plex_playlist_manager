from flask import Blueprint, current_app, render_template
from sqlalchemy import asc

from ...database import db
from ...models.plex_data_models import Playlist, PlaylistType
from ...plex import data as plex_data

index_bp = Blueprint("index", __name__)
playlist_manager_bp = Blueprint("playlist_manager", __name__)


@playlist_manager_bp.route("/main_2")
def playlist_manager():
    playlist_types = db.session.query(PlaylistType).all()
    playlists_by_type = {}
    for playlist_type in playlist_types:
        playlists_by_type[playlist_type.name] = (
            db.session.query(Playlist).filter_by(playlist_type_id=playlist_type.id).all()
        )
    return render_template(
        "playlist_manager.html", playlist_types=playlist_types, playlists_by_type=playlists_by_type
    )


@index_bp.route("/")
def index():
    plex_service = current_app.config["PLEX_SERVICE"]
    server_name = plex_service.server_name
    return render_template("index.html", server_name=server_name)
