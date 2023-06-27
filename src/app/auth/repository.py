from dependency_injector.wiring import Provide
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import async_scoped_session

from core.repository.base import BaseRepo

from .models import Token

session: async_scoped_session = Provide["session"]


class TokenRepository(BaseRepo[Token]):
    Model = Token

    @classmethod
    async def get_token_instance(cls, token: str) -> Token | None:
        query = select(cls.Model).where(and_(cls.Model.refresh_token == token))
        result = await session.execute(query)
        return result.scalars().first()

    @classmethod
    async def make_all_token_invalid(cls, user_id):
        stmt = (
            update(cls.Model)
            .where(and_(cls.Model.user_id == user_id, cls.Model.is_valid == True))
            .values(is_valid=False)
        )
        await session.execute(stmt)
