import inspect
from typing import Callable

from application.core.helpers.cache.base import BaseKeyMaker


class CustomKeyMaker(BaseKeyMaker):
    async def make(self, function: Callable, prefix: str) -> str:
        if (module := inspect.getmodule(function)) is not None:
            path = f"{prefix}::{module.__name__}.{function.__name__}"
        else:
            path = "function.__name__"
        args = ""

        for arg in inspect.signature(function).parameters.values():
            args += arg.name

        if args:
            return f"{path}.{args}"

        return path
