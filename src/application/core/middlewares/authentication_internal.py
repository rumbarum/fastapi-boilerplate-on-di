import logging
from typing import Tuple

import jwt
from dependency_injector.wiring import Provide
from starlette.authentication import AuthenticationBackend, BaseUser
from starlette.requests import HTTPConnection

from application.core.exceptions import TokenException
from application.domain.user.service import UserService

from ..exceptions.middleware import NoAuthenticationException
from .authentication_external import AuthCredentials, AuthUser

logger = logging.getLogger(__name__)


class InternalAuthBackend(AuthenticationBackend):
    async def authenticate(
        self,
        conn: HTTPConnection,
        user_service: UserService = Provide["user_container.user_service"],
    ) -> Tuple[AuthCredentials, BaseUser] | None:

        current_user = AuthUser()
        auth_credential = AuthCredentials()
        authorization: str | None = conn.headers.get("Authorization")
        if not authorization:
            current_user.auth_error = NoAuthenticationException()
            return auth_credential, current_user

        try:
            scheme, credentials = authorization.split(" ")
            if scheme.lower() != "bearer":
                current_user.auth_error = TokenException("NO_BEARER")
                return auth_credential, current_user
        except ValueError as e:
            current_user.auth_error = TokenException(e)
            return auth_credential, current_user

        if not credentials:
            current_user.auth_error = TokenException("NO_TOKEN_VALUE")
            return auth_credential, current_user

        try:
            payload = jwt.decode(
                jwt=credentials,
                key=Provide["config.JWT_SECRET_KEY"],
                algorithms=Provide["config.JWT_ALGORITHM"],
            )
            user_id = payload.get("user_id")
            token_scope = scope if (scope := payload.get("scope")) is not None else []
        except jwt.exceptions.PyJWTError as e:
            current_user.auth_error = e
            return auth_credential, current_user

        current_user.user_id = user_id
        current_user.user_authority = await user_service.get_authority(user_id=user_id)
        auth_credential.scopes = token_scope
        return auth_credential, current_user
