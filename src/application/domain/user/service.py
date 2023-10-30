from typing import List, Optional

import bcrypt
from dependency_injector.wiring import Provide, inject
from sqlalchemy.ext.asyncio import async_scoped_session

from application.core.base_class.service import BaseService
from application.core.db import Transactional
from application.domain.auth.service import TokenService

from .exceptions import (
    DuplicateEmailOrNicknameException,
    NoEmailOrWrongPassword,
    PasswordDoesNotMatchException,
    UserNotFoundException,
)
from .models import LoginResponseSchema, User
from .repository import UserAlchemyRepository

session: async_scoped_session = Provide["session"]


def hash_password(password: str) -> str:
    byte_password = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(byte_password, salt)
    return hashed_password.decode("utf-8")


def check_password(hashed_password: str, user_password: str) -> bool:
    byte_password = user_password.encode("utf-8")
    return bcrypt.checkpw(byte_password, hashed_password.encode("utf-8"))


class UserService(BaseService):
    repository: UserAlchemyRepository

    def __init__(self, repository):
        super().__init__(repository)

    async def get_user_list(
        self,
        limit: int = 12,
        prev: Optional[int] = None,
    ) -> List[User]:
        return self.repository.get_user_list(limit=limit, prev=prev)

    @Transactional()
    async def create_user(
        self, email: str, password1: str, password2: str, nickname: str
    ) -> None:
        if password1 != password2:
            raise PasswordDoesNotMatchException
        hashed_password = hash_password(password1)

        exist_user = await self.repository.get_user_by_email_or_nickname(
            email=email, nickname=nickname
        )
        if exist_user:
            raise DuplicateEmailOrNicknameException

        await self.repository.save_user(
            email=email, hashed_password=hashed_password, nickname=nickname
        )

    async def is_admin(self, user_id: int) -> bool:
        user = await self.repository.get_by_id(id=user_id)
        if not user:
            return False
        if user.is_admin is False:
            return False
        return True

    async def get_authority(self, user_id: int) -> None | str:
        user = await self.repository.get_by_id(id=user_id)
        if not user:
            return None
        return user.authority

    @inject
    async def login(
        self,
        email: str,
        password: str,
        token_service: TokenService = Provide["token_container.token_service"],
    ) -> LoginResponseSchema:
        user = await self.repository.get_user_by_email(email=email)
        if not user:
            raise UserNotFoundException
        if not check_password(user.password, password):
            raise NoEmailOrWrongPassword

        access_token, refresh_token = await token_service.issue_token(user.id)
        response = LoginResponseSchema(
            access_token=access_token, refresh_token=refresh_token
        )
        return response
