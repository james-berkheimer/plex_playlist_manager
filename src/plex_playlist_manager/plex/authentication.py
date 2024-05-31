import copy
import inspect
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.logging import LOGGER


class Authentication:
    def __init__(self, auth_data: Optional[Dict[str, Any]] = None) -> None:
        plex_cred = os.getenv("PLEX_CRED")
        if not plex_cred:
            raise ValueError("PLEX_CRED environment variable not set")

        plex_cred_path = Path(plex_cred)
        if not plex_cred_path.exists():
            raise ValueError(f"Credentials file not found: {plex_cred_path}")

        self.auth_file_path = plex_cred_path / "credentials.json"
        self.auth_data = auth_data if auth_data is not None else self._resolve_auth()
        LOGGER.debug(f"Authentication initialized with auth_data: {self._mask_auth_data()}")

    def _resolve_auth(self) -> Dict[str, Any]:
        if not os.path.exists(self.auth_file_path):
            LOGGER.error(f"Credentials file not found: {self.auth_file_path}")
            raise ValueError(f"Credentials file not found: {self.auth_file_path}")

        with open(self.auth_file_path) as auth_file:
            return json.load(auth_file)

    def _mask_auth_data(self) -> Dict[str, Any]:
        # Mask sensitive data in auth_data for logger
        masked_auth_data = copy.deepcopy(self.auth_data)
        for service in masked_auth_data:
            for key in masked_auth_data[service]:
                if "token" in key or "key" in key:
                    masked_auth_data[service][key] = "****"
        return masked_auth_data


class PlexAuthentication(Authentication):
    def __init__(self, baseurl: Optional[str] = None, token: Optional[str] = None) -> None:
        caller_frame = inspect.stack()[1]
        caller_module = inspect.getmodule(caller_frame[0])
        caller_name = caller_module.__name__ if caller_module else "unknown"
        LOGGER.debug(f"PlexAuthentication was called by {caller_name}")

        if baseurl and token:
            auth_data = {"plex": {"baseurl": baseurl, "token": token}}
        else:
            auth_data = None
            LOGGER.debug(
                "No auth data provided for PlexAuthentication, falling back to credentials.json"
            )

        super().__init__(auth_data=auth_data)
        # LOGGER.info("PlexAuthentication initialized")
        LOGGER.info(f"PlexAuthentication initialized by {caller_name}")

    @property
    def baseurl(self) -> str:
        return self.auth_data["plex"]["baseurl"]

    @property
    def token(self) -> str:
        return self.auth_data["plex"]["token"]
