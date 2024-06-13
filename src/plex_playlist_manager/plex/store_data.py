from __future__ import annotations

from redis import ConnectionError, RedisError, StrictRedis, TimeoutError

from ..utils.logging import setup_logger
from .data import get_playlist_data

logger = setup_logger()


class RedisPlexDB(StrictRedis):
    def __init__(
        self,
        plex_server,
        host: str = "localhost",
        port: int = 6379,
        decode_responses: bool = True,
    ) -> None:
        if not host:
            raise ValueError("Host must be provided")
        if not isinstance(port, int) or port <= 0:
            raise ValueError("Port must be a positive integer")

        super().__init__(host=host, port=port, decode_responses=decode_responses)
        self.plex_db = get_playlist_data(plex_server)

    def make_db(self) -> None:
        try:
            with self.pipeline() as pipe:
                for playlist_type, playlists in self.plex_db.items():
                    for playlist_title, playlist_items in playlists.items():
                        pipe.hset(playlist_type, playlist_title, str(playlist_items))
                pipe.execute()
            logger.info("Database created successfully")
        except ConnectionError:
            logger.error("Could not connect to Redis server")
            raise
        except TimeoutError:
            logger.error("Redis command timed out")
            raise
        except RedisError as e:
            logger.error("An unexpected Redis error occurred: %s", e)
            raise

    def delete_db(self) -> None:
        try:
            self.flushdb()
            logger.info("Database deleted successfully")
        except ConnectionError:
            logger.error("Could not connect to Redis server")
            raise
        except TimeoutError:
            logger.error("Redis command timed out")
            raise
        except RedisError as e:
            logger.error("An unexpected Redis error occurred: %s", e)
            raise
