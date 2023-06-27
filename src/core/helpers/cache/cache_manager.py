from functools import wraps
from typing import Optional

from dependency_injector.wiring import Provide, inject

from .base import BaseBackend, BaseKeyMaker
from .cache_tag import CacheTag


class CacheManager:
    def __init__(
        self,
        backend: BaseBackend,
        key_maker: BaseKeyMaker,
    ) -> None:
        self.backend = backend
        self.key_maker = key_maker

    async def remove_by_tag(self, tag: CacheTag) -> None:
        if self.backend is not None:
            await self.backend.delete_startswith(value=tag.value)

    async def remove_by_prefix(self, prefix: str) -> None:
        if self.backend is not None:
            await self.backend.delete_startswith(value=prefix)


def cached(
    tag: CacheTag = CacheTag.DEFAULT, prefix: Optional[str] = None, ttl: int = 60
):
    def _cached(function):
        @wraps(function)
        @inject
        async def __cached(
            *args,
            cache_manager: CacheManager = Provide["cache_manager"],
            **kwargs,
        ):
            key = await cache_manager.key_maker.make(
                function=function,
                prefix=prefix if prefix is not None else tag.value,
            )
            cached_response = await cache_manager.backend.get(key=key)
            if cached_response:
                return cached_response

            response = await function(*args, **kwargs)
            await cache_manager.backend.set(response=response, key=key, ttl=ttl)
            return response

        return __cached

    return _cached
