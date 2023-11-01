from typing import List, Type

from dependency_injector.wiring import Provide
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import async_scoped_session

from application.core.base_class.repository import BaseAlchemyRepository
from application.core.db import standalone_session

from .models import User

session: async_scoped_session = Provide["session"]


class UserAlchemyRepository(BaseAlchemyRepository[User]):
    model: Type[User]

    def __init__(self, model):
        super().__init__(model)

    @standalone_session
    async def get_user_list(
        self, limit: int = 12, prev: int | None = None
    ) -> List[User]:
        query = select(self.model)  # type: ignore[arg-type]

        if prev is not None:
            if self.model.id is not None:
                query = query.where(self.model.id < prev)

        if limit > 12:
            limit = 12

        query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @standalone_session
    async def get_user_by_email(self, email: str) -> User | None:
        query = select(self.model).filter(self.model.email == email)  # type: ignore[arg-type]
        result = await session.execute(query)
        return result.scalars().first()

    @standalone_session
    async def get_user_by_email_or_nickname(
        self, email: str, nickname: str
    ) -> User | None:
        query = select(self.model).where(or_(self.model.email == email, self.model.nickname == nickname))  # type: ignore[arg-type]
        result = await session.execute(query)
        return result.scalars().first()

    @standalone_session
    async def save_user(self, email: str, hashed_password, nickname: str) -> None:
        user = self.model(email=email, password=hashed_password, nickname=nickname)
        session.add(user)
