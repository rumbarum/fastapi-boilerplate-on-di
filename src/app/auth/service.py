from datetime import datetime

from dependency_injector.wiring import Provide

from core.db import Transactional
from core.utils.token_helper import TokenHelper

from .exceptions import TokenDecodeException, TokenExpireException
from .models import Token
from .repository import TokenRepository


class TokenService:
    Repository: TokenRepository
    """
    Token Related Service 
    """

    @classmethod
    async def issue_token(
        cls,
        user_id: int,
        access_token_exp_in: int = Provide["ACCESS_TOKEN_EXPIRE_SECONDS"],
        refresh_token_exp_in: int = Provide["REFRESH_TOKEN_EXPIRE_SECONDS"],
    ) -> tuple:
        access_token = TokenHelper.encode(
            payload={"user_id": user_id}, expire_period=access_token_exp_in
        )
        refresh_token = TokenHelper.encode(
            payload={"sub": "refresh"}, expire_period=refresh_token_exp_in
        )
        token_model = Token(user_id=user_id, refresh_token=refresh_token)
        await cls.Repository.save(token_model)
        return access_token, refresh_token

    @classmethod
    @Transactional()
    async def refresh_access_token(
        cls,
        refresh_token: str,
        refresh_expire_in: int = Provide["REFRESH_TOKEN_EXPIRE_SECONDS"],
    ):
        decoded_refresh_token = TokenHelper.decode(token=refresh_token)
        if decoded_refresh_token.get("sub") != "refresh":
            raise TokenDecodeException

        token_instance = await cls.Repository.get_token_instance(refresh_token)
        if (
            token_instance is not None
            and (exp := token_instance.refresh_expires_at) is not None
            and exp > datetime.utcnow()
        ):
            new_access_token = TokenHelper.encode(
                payload={"user_id": token_instance.user_id},
                expire_period=refresh_expire_in,
            )
            return new_access_token
        raise TokenExpireException

    @classmethod
    async def revoke_refresh_token(cls, user_id: int) -> None:
        await cls.Repository.make_all_token_invalid(user_id)