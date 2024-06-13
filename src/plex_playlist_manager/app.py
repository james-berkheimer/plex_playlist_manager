from flask import Flask

from .apps.playlist_manager.routes import get_playlist_items_bp, playlist_manager_bp


def create_app():
    app = Flask(__name__)

    # Register the blueprint with the app
    app.register_blueprint(get_playlist_items_bp)
    app.register_blueprint(playlist_manager_bp)

    return app


app = create_app()
