from datetime import datetime, timedelta

import jwt
from dependency_injector.wiring import Provide, inject

from application.core.exceptions.token import TokenDecodeException, TokenExpireException


class TokenHelper:
    @staticmethod
    @inject
    def encode(
        payload: dict,
        expire_period: int,
        jwt_secret_key: str = Provide["config.JWT_SECRET_KEY"],
        jwt_algorithm: str = Provide["config.JWT_ALGORITHM"],
    ) -> str:
        token = jwt.encode(  # type: ignore[attr-defined]
            payload={
                **payload,
                "exp": datetime.utcnow() + timedelta(seconds=expire_period),
            },
            key=jwt_secret_key,
            algorithm=jwt_algorithm,
        )
        return token

    @staticmethod
    @inject
    def decode(
        token: str,
        jwt_secret_key=Provide["config.JWT_SECRET_KEY"],
        jwt_algorithm=Provide["config.JWT_ALGORITHM"],
    ) -> dict:
        try:
            return jwt.decode(
                token,
                jwt_secret_key,
                jwt_algorithm,
            )
        except jwt.exceptions.DecodeError:
            raise TokenDecodeException
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpireException

    @staticmethod
    @inject
    def decode_expired_token(
        token: str,
        jwt_secret_key=Provide["config.JWT_SECRET_KEY"],
        jwt_algorithm=Provide["config.JWT_ALGORITHM"],
    ) -> dict:
        try:
            return jwt.decode(
                token,
                jwt_secret_key,
                jwt_algorithm,
                options={"verify_exp": False},
            )
        except jwt.exceptions.DecodeError:
            raise TokenDecodeException
