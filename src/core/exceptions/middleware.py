from http import HTTPStatus

from core.enums import ResponseCode
from core.exceptions import AuthException


class NoAuthenticationException(AuthException):
    http_code = HTTPStatus.UNAUTHORIZED
    error_code = ResponseCode.NO_AUTHENTICATION
    message = ResponseCode.NO_AUTHENTICATION.message


class NoAuthorityException(AuthException):
    http_code = HTTPStatus.UNAUTHORIZED
    error_code = ResponseCode.NO_AUTHORITY
    message = ResponseCode.NO_AUTHORITY.message
