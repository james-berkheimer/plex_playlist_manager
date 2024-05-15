from flask import render_template

from .. import plex_playlist_manager  # assuming your Flask application is named "app"


@plex_playlist_manager.route("/")
def home():
    return render_template("gui.html")
