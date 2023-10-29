from application.core.exceptions import CustomException


class UserDomainException(CustomException):
    pass


class PasswordDoesNotMatchException(UserDomainException):
    http_code = 401
    error_code = 401
    message = "password does not match"


class DuplicateEmailOrNicknameException(UserDomainException):
    http_code = 400
    error_code = 400
    message = "duplicate email or nickname"


class UserNotFoundException(UserDomainException):
    http_code = 404
    error_code = 404
    message = "user not found"


class NoEmailOrWrongPassword(UserDomainException):
    http_code = 400
    error_code = 400
    message = "no email or wrong password"
