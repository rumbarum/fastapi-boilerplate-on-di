from dependency_injector.wiring import Provide
from sqlalchemy.ext.asyncio import async_scoped_session

from core.base_class.service import BaseService
from core.db import standalone_session

from .models import RequestResponseLog
from .repository import RequestResponseLogRepository

session: async_scoped_session = Provide["session"]


class BaseLogHandler:
    async def __call__(self, *args, **kwargs):
        raise NotImplementedError


class DatabaseLoghandler(BaseLogHandler, BaseService):
    repository: RequestResponseLogRepository

    def __init__(self, repository):
        super().__init__()
        self.repository = repository

    @standalone_session
    async def __call__(self, data: dict):
        request_response_log = RequestResponseLog(**data)
        self.repository.save(request_response_log)
