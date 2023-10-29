from abc import ABC
from http import HTTPStatus

from application.core.enums import ResponseCode


class CustomException(ABC, Exception):
    """AbstractException"""

    http_code: int
    error_code: int
    message: str

    def __init__(self, message=None):
        if message:
            self.message = message


# Root classification
class ExternalServiceException(CustomException):
    http_code: int = HTTPStatus.BAD_REQUEST
    error_code: int = ResponseCode.EXTERNAL_SERVICE_CLIENT_ERROR
    message: str = ResponseCode.EXTERNAL_SERVICE_SERVER_ERROR.message


class AuthException(CustomException):
    http_code: int = HTTPStatus.UNAUTHORIZED
    error_code: int = ResponseCode.NO_AUTHORITY
    message: str = ResponseCode.NO_AUTHORITY.message


class TokenException(CustomException):
    http_code: int = HTTPStatus.BAD_REQUEST
    error_code: int = ResponseCode.TOKEN_INVALID
    message: str = ResponseCode.TOKEN_INVALID.message


class HttpException(CustomException):
    http_code: int = HTTPStatus.BAD_REQUEST
    error_code: int = ResponseCode.BASIC_HTTP_ERROR
    message: str = ResponseCode.BASIC_HTTP_ERROR.message
