from dependency_injector.wiring import Provide
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import async_scoped_session

from application.core.db import standalone_session
from application.core.repository.alchemy_repository import BaseAlchemyRepository

from .models import Token

session: async_scoped_session = Provide["session"]


class TokenAlchemyRepository(BaseAlchemyRepository[Token, int]):
    model: type[Token]

    def __init__(self, model):
        super().__init__(model)

    @standalone_session
    async def get_token_instance(self, token: str) -> Token | None:
        query = select(self.model).filter(self.model.refresh_token == token)
        result = await session.execute(query)
        return result.scalars().first()

    @standalone_session
    async def make_all_token_invalid(self, user_id):
        stmt = (
            update(self.model)
            .where(and_(self.model.user_id == user_id, self.model.is_valid == True))
            .values(is_valid=False)
        )
        await session.execute(stmt)
