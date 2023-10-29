from dependency_injector.wiring import Provide
from sqlalchemy.ext.asyncio import async_scoped_session

from application.core.base_class.repository import BaseRepository

from .models import YourModel

session: async_scoped_session = Provide["session"]


class YourRepository(BaseRepository):
    model: type[YourModel]

    def __init__(self, model):
        super().__init__(model)
