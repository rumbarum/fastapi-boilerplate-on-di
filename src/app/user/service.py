from typing import List, Optional

import bcrypt
from dependency_injector.wiring import Provide
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import async_scoped_session

from app.auth.service import TokenService
from core.db import Transactional

from .exceptions import (
    DuplicateEmailOrNicknameException,
    NoEmailOrWrongPassword,
    PasswordDoesNotMatchException,
    UserNotFoundException,
)
from .models import LoginResponseSchema, User

session: async_scoped_session = Provide["session"]


def hash_password(password: str) -> str:
    byte_password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(byte_password, salt)
    return hashed_password.decode("utf-8")


def check_password(hashed_password: str, user_password: str) -> bool:
    byte_password = user_password.encode("utf-8")
    return bcrypt.checkpw(byte_password, hashed_password.encode("utf-8"))


class UserService:
    def __init__(self):
        ...

    async def get_user_list(
        self,
        limit: int = 12,
        prev: Optional[int] = None,
    ) -> List[User]:
        query = select(User)  # type: ignore[arg-type]

        if prev:
            query = query.where(User.id < prev)

        if limit > 12:
            limit = 12

        query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @Transactional()
    async def create_user(
        self, email: str, password1: str, password2: str, nickname: str
    ) -> None:
        if password1 != password2:
            raise PasswordDoesNotMatchException

        query = select(User).where(or_(User.email == email, User.nickname == nickname))  # type: ignore[arg-type]
        result = await session.execute(query)
        is_exist = result.scalars().first()
        if is_exist:
            raise DuplicateEmailOrNicknameException

        hashed_password = hash_password(password1)
        user = User(email=email, password=hashed_password, nickname=nickname)
        session.add(user)

    async def is_admin(self, user_id: int) -> bool:
        result = await session.execute(select(User).where(User.id == user_id))  # type: ignore[arg-type]
        user = result.scalars().first()
        if not user:
            return False

        if user.is_admin is False:
            return False

        return True

    async def get_authority(self, user_id: int) -> None | str:
        result = await session.execute(select(User).where(User.id == user_id))  # type: ignore[arg-type]
        user = result.scalars().first()
        if not user:
            return None
        return user.authority

    async def login(
        self,
        email: str,
        password: str,
    ) -> LoginResponseSchema:
        result = await session.execute(
            select(User).where(and_(User.email == email))  # type: ignore[arg-type]
        )
        user = result.scalars().first()
        if not user:
            raise UserNotFoundException
        if not check_password(user.password, password):
            raise NoEmailOrWrongPassword

        access_token, refresh_token = await TokenService.issue_token(
            user.id
        )

        response = LoginResponseSchema(
            access_token=access_token, refresh_token=refresh_token
        )
        return response
