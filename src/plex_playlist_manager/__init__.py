import os
from pathlib import Path

from plexapi.server import PlexServer

from .plex.authentication import PlexAuthentication

project_root = Path(__file__).resolve().parent.parent.parent
os.environ["PLEX_CRED"] = str(project_root / "tests/.plex_cred")

plex_auth = PlexAuthentication()
plex_server = PlexServer(baseurl=plex_auth.baseurl, token=plex_auth.token)
