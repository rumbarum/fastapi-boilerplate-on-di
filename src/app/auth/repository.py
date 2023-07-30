from dependency_injector.wiring import Provide
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import async_scoped_session

from core.base_class.repository import BaseRepository

from .models import Token

session: async_scoped_session = Provide["session"]


class TokenRepository(BaseRepository[Token]):
    model: Token

    def __init__(self, model):
        super().__init__(model)

    async def get_token_instance(self, token: str) -> Token | None:
        query = select(self.model).where(and_(self.model.refresh_token == token))
        result = await session.execute(query)
        return result.scalars().first()

    async def make_all_token_invalid(self, user_id):
        stmt = (
            update(self.model)
            .where(and_(self.model.user_id == user_id, self.model.is_valid == True))
            .values(is_valid=False)
        )
        await session.execute(stmt)
