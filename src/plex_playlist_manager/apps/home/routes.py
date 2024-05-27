from flask import Blueprint, current_app, render_template

from ...database import db
from ...models.plex_data_models import Playlist
from ...plex import data as plex_data

index_bp = Blueprint("index", __name__)
playlist_manager_bp = Blueprint("playlist_manager", __name__)


@playlist_manager_bp.route("/main_2")
def playlist_manager():
    playlist_data = db.session.query(Playlist).all()
    return render_template("playlist_manager.html", playlist_data=playlist_data)


@index_bp.route("/")
def index():
    plex_service = current_app.config["PLEX_SERVICE"]
    server_name = plex_service.server_name
    return render_template("index.html", server_name=server_name)
