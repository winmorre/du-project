import traceback

import structlog
from redis.asyncio import Redis, RedisError
from account_serv import settings

Logger = structlog.getLogger(__name__)
REDIS_PREFIX = "REDIS"


class RedisConnectionHandler:
    """Redis connection handler to connect to redis cluster or instance.
    raised RedisError if connection not established
    """

    def __init__(self, db, port, redis_url, password, host):
        try:
            if redis_url is not None or str(redis_url).strip() != "":
                self.__redis_client = Redis.from_url(url=redis_url, decode_responses=True)
            else:
                self.__redis_client = Redis(
                    host=host,
                    port=port,
                    password=password,
                    encoding="utf-8",
                    db=db,
                )
        except RedisError:
            Logger.error("Redis connection error", host=host, url=redis_url, port=port,
                         traceback=traceback.format_exc())

    @property
    def redis(self):
        return self.__redis_client


redis_config = settings.REDIS_CONFIG


def create_redis_connection(db=None, host=None, port=None, password=None, url=None):
    connection = RedisConnectionHandler(
        db=db or redis_config.db,
        host=host or redis_config.host,
        port=port or redis_config.port,
        password=password or redis_config.password,
        redis_url=url or redis_config.url
    )

    try:
        yield connection.redis
    finally:
        connection.redis.close()
