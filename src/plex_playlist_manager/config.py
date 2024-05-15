from plexapi.server import PlexServer

from .utils.authentication import PlexAuthentication
from .utils.logging import setup_logger

LOGGER = setup_logger("Flask Logger")
plex_auth = PlexAuthentication()
PLEX = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)
