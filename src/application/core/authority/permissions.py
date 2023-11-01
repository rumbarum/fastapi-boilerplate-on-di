from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Type

from starlette.requests import Request

from application.core.exceptions import CustomException
from application.core.exceptions.middleware import (
    NoAuthenticationException,
    NoAuthorityException,
)
from application.core.middlewares import AuthUser


class Authority(StrEnum):
    level: int
    description: str

    MASTER = ("MASTER", 0, "master account")
    ADMIN = ("ADMIN", 1, "admin account")
    USER = ("USER", 2, "user account")
    GUEST = ("GUEST", 3, "guest account")

    def __new__(cls, value, level, description=""):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.level = level  # type: ignore
        obj.description = description  # type: ignore
        return obj

    @classmethod
    def is_authority_higher_or_equal_than_prior(cls, auth1: str, auth2: str) -> bool:
        """lowest is higher priority"""
        return cls[auth1].level >= cls[auth2].level

    @classmethod
    def is_authority_higher_than_prior(cls, auth1: str, auth2: str) -> bool:
        """lowest is higher priority"""
        return cls[auth1].level > cls[auth2].level


class BasePermission(ABC):
    exception: Type[CustomException]

    @abstractmethod
    async def has_permission(self, request: Request) -> bool:
        pass


class IsAuthenticated(BasePermission):
    exception = NoAuthenticationException

    async def has_permission(self, request: Request) -> bool:
        user: AuthUser = request.user
        if user.auth_error is not None:
            raise user.auth_error
        return user.is_authenticated


class IsMaster(BasePermission):
    allowed_authority = Authority.MASTER.name
    exception = NoAuthorityException

    async def has_permission(self, request: Request) -> bool:
        user: AuthUser = request.user
        if user.auth_error is not None:
            raise user.auth_error
        if (auth := user.user_authority) is not None and auth == self.allowed_authority:
            return True
        return False


class IsAdmin(IsMaster):
    allowed_authority = Authority.ADMIN.name


class IsUser(IsMaster):
    allowed_authority = Authority.USER.name


class IsGuest(IsMaster):
    allowed_authority = Authority.GUEST.name


class IsHigherOrEqualMaster(BasePermission):
    allowed_authority = Authority.MASTER.name
    exception = NoAuthorityException

    async def has_permission(self, request: Request) -> bool:
        user: AuthUser = request.user
        if user.auth_error is not None:
            raise user.auth_error
        if (
            auth := user.user_authority
        ) is not None and Authority.is_authority_higher_or_equal_than_prior(
            self.allowed_authority, auth
        ):
            return True
        return False


class IsHigherOrEqualAdmin(IsHigherOrEqualMaster):
    allowed_authority = Authority.ADMIN.name


class IsHigherOrEqualUser(IsHigherOrEqualMaster):
    allowed_authority = Authority.USER.name


class IsHigherOrEqualGuest(IsHigherOrEqualMaster):
    allowed_authority = Authority.GUEST.name


class AllowAll(BasePermission):
    async def has_permission(self, request: Request) -> bool:
        return True
