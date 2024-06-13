from __future__ import annotations

import json
from typing import Any, Dict

from redis import ConnectionError, RedisError, StrictRedis, TimeoutError

from ..utils.logging import setup_logger

logger = setup_logger()


def make_db(redis: StrictRedis, plex_db: Dict[str, Any]) -> None:
    try:
        with redis.pipeline() as pipe:
            for playlist_type, playlists in plex_db.items():
                for playlist_title, playlist_items in playlists.items():
                    json_items = json.dumps(playlist_items)
                    pipe.hset(playlist_type, playlist_title, json_items)
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


def get_db(host="localhost", port=6379, db=0):
    """
    Returns a Redis database instance.

    Parameters:
    host (str): The host of the Redis server. Default is 'localhost'.
    port (int): The port of the Redis server. Default is 6379.
    db (int): The database number to connect to. Default is 0.

    Returns:
    StrictRedis: The Redis database instance.
    """
    return StrictRedis(host=host, port=port, db=db)


def delete_db(redis: StrictRedis) -> None:
    try:
        redis.flushdb()
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
