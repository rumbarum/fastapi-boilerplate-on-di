from http import HTTPStatus

from application.core.enums import ResponseCode
from application.core.exceptions import ExternalServiceException


class ExternalServiceClientException(ExternalServiceException):
    http_code = HTTPStatus.BAD_REQUEST
    error_code = ResponseCode.EXTERNAL_SERVICE_CLIENT_ERROR
    message = ResponseCode.EXTERNAL_SERVICE_CLIENT_ERROR.message


class ExternalServiceServerException(ExternalServiceException):
    http_code = HTTPStatus.BAD_REQUEST
    error_code = ResponseCode.EXTERNAL_SERVICE_SERVER_ERROR
    message = ResponseCode.EXTERNAL_SERVICE_SERVER_ERROR.message
