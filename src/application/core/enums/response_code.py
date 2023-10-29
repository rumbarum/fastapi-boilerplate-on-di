from enum import IntEnum


class ResponseCode(IntEnum):
    """
    ## sample
    ResponseCode.OK ==> 2000
    ResponseCode.OK.message ==> "Request Success"
    ResponseCode.OK.description ==> ""

    Response code
     status codes and reason phrases

     response format
     {
        "code" : 2000,
        "message" : "Request Success",
        "data": {...}
    }
    """

    message: str
    description: str

    def __new__(cls, value, message, description=""):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.message = message  # type: ignore
        obj.description = description  # type: ignore
        return obj

    # informational
    OK = (200, "Request succeed")
    CREATED = (201, "Created", "Document created, URL follows")
    ACCEPTED = (202, "Accepted")

    # auth related

    AUTH_SERVER_NOT_RESPONDING = (2000, "Auth server not responding")
    NO_AUTHENTICATION = (2001, "No Authentication")
    INVALID_ACCESS_TOKEN = (2002, "Invalid access token")
    TOKEN_ISSUE_FAIL = (2003, "Token issue fail")

    NO_AUTHORITY = (2101, "No Authority")

    # request related
    INVALID_REQUEST_PARAM = (3000, "Invalid request param")
    NOT_NULLABLE_REQUEST_PARAM = (3001, "Not nullable param get null value")
    RUNTIME_ERROR = (3002, "Runtime error")
    # http related
    BASIC_HTTP_ERROR = (3003, "Check HTTP status code")
    UNDEFINED_ERROR = (3004, "Undefined error")

    # AUTH Server Response Code
    INVALID_PARAM = (4001, "Invalid param", "No 'token' key")
    WRONG_TOKEN_TYPE = (4002, "Wrong token type")
    TOKEN_INVALID = (4003, "Wrong token")
    TOKEN_NOT_EXIST = (4004, "Token is not exist")
    TOKEN_EXPIRED = (4005, "Token is expired")
    TOKEN_REVOKED = (4006, "Token is revoked")

    EXTERNAL_SERVICE_CLIENT_ERROR = (
        5001,
        "External service request wrongly",
    )
    EXTERNAL_SERVICE_SERVER_ERROR = (5002, "External service error")
