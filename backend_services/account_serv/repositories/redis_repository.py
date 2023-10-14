import json
from typing import Optional

from django.conf import settings
from redis.asyncio import Redis

_settings = settings.REDIS_CONFIG


class RedisRepository:
    __slots__ = ("_redis",)

    def __init__(self, redis: Redis):
        self._redis = redis

    async def set_item_with_expiration(self, item_id, data, ttl=None):
        result = self._redis.setex(name=str(item_id), time=ttl or _settings.ttl, value=json.dumps(data))
        return result

    async def set_item(self, item_id, item):
        result = await self._redis.set(str(item_id), json.dumps(item))
        return result

    async def delete_item(self, item_id):
        result = 0
        if self._redis.exists(str(item_id)):
            result = await self._redis.delete(str(item_id))
        return result

    async def get_item_and_set_expiration(self, item_id, ttl=None):
        data: Optional[str | bytes] = await self._redis.getex(str(item_id), ttl or _settings.ttl)
        if data is not None:
            return json.loads(data)
        return None
