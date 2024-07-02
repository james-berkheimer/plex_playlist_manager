import json
import os

from plexapi.server import PlexServer

from .plex.authentication import (
    AuthenticationError,
    PlexAuthentication,
)
from .utils.logging import LOGGER

cred_path = (
    "/home/james/code/plex_playlist_manager/tests/.plex_cred/credentials.json"  # for development
)


def set_env_vars_from_json(cred_path):
    with open(cred_path, "r") as f:
        data = json.load(f)
        plex_data = data.get("plex", {})
        os.environ["PLEX_BASEURL"] = plex_data.get("baseurl", "")
        os.environ["PLEX_TOKEN"] = plex_data.get("token", "")
        LOGGER.debug(
            "Environment variables set: PLEX_BASEURL = %s , PLEX_TOKEN = %s",
            os.environ["PLEX_BASEURL"],
            os.environ["PLEX_TOKEN"],
        )


# Set environment variables from the JSON credentials file
set_env_vars_from_json(cred_path)

# Initialize Plex Authentication
try:
    plex_auth = PlexAuthentication()
    # Create the Plex Server instance
    plex_server = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)
except AuthenticationError as e:
    raise RuntimeError("Failed to initialize Plex server") from e
