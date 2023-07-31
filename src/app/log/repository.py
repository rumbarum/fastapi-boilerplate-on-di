from typing import Type

from dependency_injector.wiring import Provide
from sqlalchemy.ext.asyncio import async_scoped_session

from core.base_class.repository import BaseRepository

from .models import RequestResponseLog

session: async_scoped_session = Provide["session"]


class RequestResponseLogRepository(BaseRepository[RequestResponseLog]):
    model: Type[RequestResponseLog]

    def __init__(self, model):
        super().__init__(model)
