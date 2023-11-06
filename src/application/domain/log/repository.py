from dependency_injector.wiring import Provide
from sqlalchemy.ext.asyncio import async_scoped_session

from application.core.repository.alchemy_repository import BaseAlchemyRepository

from .models import RequestResponseLog

session: async_scoped_session = Provide["session"]


class RequestResponseLogAlchemyRepository(
    BaseAlchemyRepository[RequestResponseLog, int]
):
    model: type[RequestResponseLog]

    def __init__(self, model):
        super().__init__(model)
