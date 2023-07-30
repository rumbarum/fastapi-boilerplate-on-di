from http import HTTPStatus

from core.enums import ResponseCode
from core.exceptions import TokenException


class TokenDecodeException(TokenException):
    http_code = HTTPStatus.BAD_REQUEST
    error_code = ResponseCode.TOKEN_INVALID
    message = ResponseCode.TOKEN_INVALID.message


class TokenExpireException(TokenException):
    http_code = HTTPStatus.BAD_REQUEST
    error_code = ResponseCode.TOKEN_EXPIRED
    message = ResponseCode.TOKEN_EXPIRED.message


class TokenInvalidException(TokenException):
    http_code = HTTPStatus.BAD_REQUEST
    error_code = ResponseCode.TOKEN_INVALID
    message = ResponseCode.TOKEN_INVALID.message
