from enum import Enum, StrEnum


class SynchronizeSessionEnum(Enum):
    FETCH = "fetch"
    EVALUATE = "evaluate"
    FALSE = False


class OrderingEnum(StrEnum):
    ASC = "asc"
    DESC = "desc"


class FilterMethod(StrEnum):
    MATCH = "match"
    ILIKE = "ilike"
    LIKE = "like"


class FilterInOrNot(StrEnum):
    IN = "in"
    NOT_IN = "not_in"
