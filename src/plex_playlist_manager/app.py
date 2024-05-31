from flask import Flask

from .apps.home.routes import index_bp, playlist_manager_bp
from .database import db
from .plex import PlexService

# from .plex.store_data import store_playlist_data
from .plex.store_data import get_and_store_playlist_data
from .utils.logging import LOGGER


def create_tables(app, db):
    if not app.config.get("RECREATE_DB_ON_START", False):
        LOGGER.info("Skipping database table creation")
        return

    LOGGER.info("Creating database tables")
    with app.app_context():
        db.create_all()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///plex_playlist_manager.db"
    app.config["RECREATE_DB_ON_START"] = True
    db.init_app(app)

    # Import your models here
    from .models.plex_data_models import (  # noqa: E402
        Album,
        Artist,
        Episode,
        Movie,
        Playlist,
        Season,
        Show,
        Track,
    )

    # Create the database tables
    create_tables(app, db)

    # Initialize Plex Service
    plex_service = PlexService()

    # Get the server name
    # server_name = plex_service.server_name
    # print(f"Server Name: {server_name}")

    # Attach Plex Service to the app instance
    app.config["PLEX_SERVICE"] = plex_service
    # app.config["SERVER_NAME"] = server_name

    # Store playlist data in the database
    with app.app_context():
        # store_playlist_data()
        get_and_store_playlist_data()

    # Register the blueprint with the app
    app.register_blueprint(index_bp)
    app.register_blueprint(playlist_manager_bp)

    return app


app = create_app()
