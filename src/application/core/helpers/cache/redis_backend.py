import pickle
from typing import Any

import orjson
from dependency_injector.providers import Singleton
from dependency_injector.wiring import Provide
from redis.asyncio.client import Redis

from application.core.helpers.cache.base import BaseBackend


class RedisBackend(BaseBackend):

    redis_provider: Singleton[Redis] = Provide["redis.provider"]

    async def get(self, key: str) -> Any:
        redis = self.redis_provider()
        result = await redis.get(key)
        if not result:
            return

        try:
            return orjson.loads(result.decode("utf8"))
        except UnicodeDecodeError:
            return pickle.loads(result)

    async def set(self, response: Any, key: str, ttl: int = 60) -> None:
        if isinstance(response, dict):
            response = orjson.dumps(response)
        elif isinstance(response, object):
            response = pickle.dumps(response)

        redis = self.redis_provider()
        await redis.set(name=key, value=response, ex=ttl)

    async def delete_startswith(self, value: str) -> None:
        redis = self.redis_provider()
        async for key in redis.scan_iter(f"{value}::*"):
            await redis.delete(key)
