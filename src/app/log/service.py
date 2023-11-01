from dependency_injector.wiring import Provide
from sqlalchemy.ext.asyncio import async_scoped_session

from core.db import standalone_session

from .models import RequestResponseLog

session: async_scoped_session = Provide["session"]


class BaseLogHandler:
    async def __call__(self, *args, **kwargs):
        raise NotImplementedError


class DatabaseLoghandler:
    def __init__(self):
        ...

    @standalone_session
    async def __call__(self, data: dict):
        log = RequestResponseLog(**data)
        session.add(log)
