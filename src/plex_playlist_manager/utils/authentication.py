import copy
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .logging import setup_logger

logger = setup_logger()


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
        logger.info(f"Authentication initialized with auth_data: {self._mask_auth_data()}")

    def _resolve_auth(self) -> Dict[str, Any]:
        if not os.path.exists(self.auth_file_path):
            logger.error(f"Credentials file not found: {self.auth_file_path}")
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
        if baseurl and token:
            auth_data = {"plex": {"baseurl": baseurl, "token": token}}
        else:
            auth_data = None
            logger.warning(
                "No auth data provided for PlexAuthentication, falling back to credentials.json"
            )

        super().__init__(auth_data=auth_data)
        logger.info("PlexAuthentication initialized")

    @property
    def baseurl(self) -> str:
        return self.auth_data["plex"]["baseurl"]

    @property
    def token(self) -> str:
        return self.auth_data["plex"]["token"]
