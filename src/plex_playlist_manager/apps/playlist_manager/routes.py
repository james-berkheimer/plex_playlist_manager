from pprint import pprint

from flask import Blueprint, abort, render_template, request

from ...config import plex_server
from ...plex.data import categorized_playlists, playlist_data, playlist_details

# all_playlist_data = get_playlist_data(plex_server)

get_playlist_items_bp = Blueprint("get_playlist_items", __name__)
get_playlist_details_bp = Blueprint("get_playlist_details", __name__)
playlist_manager_bp = Blueprint("playlist_manager", __name__)


# def categorize_playlists():
#     try:
#         return {ptype: list(data.keys()) for ptype, data in all_playlist_data.items()}
#     except Exception as e:
#         print(f"Failed to fetch playlists: {e}")
#         return abort(500, description="Failed to categorize playlists")


@playlist_manager_bp.route("/")
def playlist_manager():
    category_dict = categorized_playlists()
    pprint(categorized_playlists)
    if categorized_playlists is None:
        return abort(500, description="Error fetching categorized playlists")
    return render_template(
        "playlist_manager/playlist_manager_main.html", category_dict=category_dict
    )


@get_playlist_items_bp.route("/get_playlist_items", methods=["POST"])
def get_playlist_items():
    request_data = request.json
    playlist_type = request_data.get("playlist_type", "").strip()
    playlist_title = request_data.get("playlist_title", "").strip()
    print(f"Playlist type: {playlist_type}, Playlist title: {playlist_title}")
    if not playlist_type or not playlist_title:
        return abort(400, description="Missing or blank playlist type or title")

    try:
        data_dict = playlist_data(playlist_type, playlist_title)
    except KeyError:
        return abort(400, description="Invalid playlist type or title")

    template = f"playlist_manager/template_{playlist_type}_playlist.html"
    return render_template(
        template,
        data_dict=data_dict,
        enumerate=enumerate if playlist_type in ["audio", "video"] else None,
    )


@get_playlist_details_bp.route("/get_playlist_details", methods=["POST"])
def get_playlist_details():
    request_data = request.json
    playlist_type = request_data.get("playlist_type", "").strip()
    playlist_title = request_data.get("playlist_title", "").strip()
    print(f"Playlist type: {playlist_type}, Playlist title: {playlist_title}")
    if not playlist_type or not playlist_title:
        return abort(400, description="Missing or blank playlist type or title")

    try:
        details_dict = playlist_details(playlist_type, playlist_title)
    except KeyError:
        return abort(400, description="Invalid playlist type or title")

    template = f"playlist_manager/template_topbar_{playlist_type}_details.html"
    return render_template(template, details_dict=details_dict)
