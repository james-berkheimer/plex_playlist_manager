from plexapi.exceptions import BadRequest
from plexapi.server import PlexServer
from requests.exceptions import RequestException

from ..utils.logging import LOGGER
from .authentication import PlexAuthentication


class PlexService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance = super(PlexService, cls).__new__(cls)
                cls._instance._plex_auth = PlexAuthentication()
                cls._instance._plex_server = PlexServer(
                    baseurl=cls._instance._plex_auth.baseurl,
                    token=cls._instance._plex_auth.token,
                )
                cls._instance._server_name = cls._instance._plex_server.friendlyName
            except (BadRequest, RequestException) as e:
                LOGGER.debug(f"Error initializing PlexService: {e}")
                cls._instance = None
        return cls._instance

    @property
    def plex_server(self):
        return self._plex_server

    @property
    def server_name(self):
        return self._server_name
