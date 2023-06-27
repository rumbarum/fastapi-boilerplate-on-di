from http import HTTPStatus

from .base import HttpException


class BadRequestException(HttpException):
    http_code = HTTPStatus.BAD_REQUEST


class NotFoundException(HttpException):
    http_code = HTTPStatus.NOT_FOUND


class ForbiddenException(HttpException):
    http_code = HTTPStatus.FORBIDDEN


class UnauthorizedException(HttpException):
    http_code = HTTPStatus.UNAUTHORIZED


class UnprocessableEntity(HttpException):
    http_code = HTTPStatus.UNPROCESSABLE_ENTITY


class DuplicateValueException(HttpException):
    http_code = HTTPStatus.UNPROCESSABLE_ENTITY
