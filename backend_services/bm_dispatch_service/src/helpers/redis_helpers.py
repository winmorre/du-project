import traceback

import structlog
from redis.asyncio import Redis, RedisError

from configs.settings import get_settings

_settings = get_settings()
Logger = structlog.getLogger(__name__)

REDIS_PREFIX = "REDIS"


class RedisConnectionHandler:
    """A connection handler for connecting to redis cluster"""

    def __init__(self, db, port, redis_url, password, host):
        try:
            if redis_url is not None or str(redis_url).strip() != "":
                self.__redis_client = Redis.from_url(url=redis_url, decode_reponse=True)
            else:
                self.__redis_client = Redis(
                    host=host,
                    port=port,
                    password=password,
                    encoding="utf-8",
                    db=db,
                )
        except RedisError:
            Logger.error("Redis connection error", host=host, url=redis_url, traceback=traceback.format_exc())

    @property
    def redis(self):
        return self.__redis_client


def create_redis_connection(db=None, host=None, port=None, password=None, url=None):
    connection = RedisConnectionHandler(
        db=db or _settings.redis_db,
        host=host or _settings.redis_host,
        port=port or _settings.redis_port,
        password=password or _settings.redis_password,
        redis_url=url or _settings.redis_url
    )
    try:
        yield connection.redis
    finally:
        connection.redis.close()
