import base64
import json
import logging
from typing import Optional, Tuple

from dependency_injector.providers import Singleton
from dependency_injector.wiring import Provide
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.authentication import AuthCredentials, AuthenticationBackend, BaseUser
from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)
from starlette.requests import HTTPConnection

from application.core.exceptions import ExternalServiceException, TokenException
from application.core.exceptions.token import TokenDecodeException
from application.core.external_service import AuthClient

from ..exceptions.middleware import NoAuthenticationException

logger = logging.getLogger(__name__)


def on_auth_error(request: Request, exc: Exception):
    """
    Dummy function.
    If there are not requiring authenticated request e.g. `/healthcheck` and auth middleware raise Exception when there is no auth info,
    no chance to handle request. So if auth middleware raise error, it is set on `request.user.auth_error`
    and when permission checks, raise Exception
    """
    status_code, error_code, message = 401, None, str(exc)
    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )


def decode_base64(encoded_string) -> dict:
    # Add padding if necessary
    padding_length = len(encoded_string) % 4
    if padding_length > 0:
        encoded_string += "=" * (4 - padding_length)

    # Decode the Base64 string
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode("utf-8")
    return json.loads(decoded_string)


class CustomAuthCredentials(AuthCredentials):
    def __init__(
        self,
        scopes: Optional[list[str]] = None,
    ):
        super().__init__(scopes)


class AuthUser(BaseUser):
    def __init__(
        self,
        user_id: int | None = None,
        group_id: int | None = None,
        user_authority: str | None = None,
    ):
        self.user_id = user_id
        self.group_id = group_id
        self.user_authority = user_authority
        self.auth_error: Exception | None = None

    def __repr__(self):
        return f"AuthUser(user_id={self.user_id}, group_id={self.group_id})"

    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None

    @property
    def display_name(self) -> str:
        return f"USER_ID: {self.user_id}"

    @property
    def identity(self) -> str:
        return self.__repr__()


class ExternalAuthBackend(AuthenticationBackend):

    auth_client_provider: Singleton[AuthClient] = Provide["auth_client.provider"]

    async def authenticate(
        self, conn: HTTPConnection
    ) -> Tuple[AuthCredentials, BaseUser] | None:
        auth_client = self.auth_client_provider()
        current_user = AuthUser()
        auth_credentials = CustomAuthCredentials()
        authorization: str | None = conn.headers.get("Authorization")
        if authorization is None:
            current_user.auth_error = NoAuthenticationException()
            return auth_credentials, current_user
        try:
            scheme, access_token = authorization.split(" ")
            if (
                (scheme.lower() != "bearer")
                or (access_token is None)
                or (not await auth_client.is_token_valid(access_token))
            ):
                current_user.auth_error = TokenDecodeException()
                return auth_credentials, current_user

            creds = access_token.split(".")
            user_info = decode_base64(creds[1])

        except ValueError as e:
            logger.info(f"TokenValueException: {e}")
            current_user.auth_error = e
            return auth_credentials, current_user
        except ExternalServiceException as e:
            logger.info(f"ExternalServiceException: {e}")
            current_user.auth_error = e
            return auth_credentials, current_user
        except TokenException as e:
            logger.info(f"TokenException: {e}")
            current_user.auth_error = e
            return auth_credentials, current_user

        auth_credentials.scopes = (
            scope if (scope := user_info.get("scope")) is not None else []
        )

        current_user.user_id = user_info.get("user_id")
        current_user.group_id = user_info.get("group_id")
        current_user.user_authority = user_info.get("user_authority")

        return auth_credentials, current_user


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    pass
