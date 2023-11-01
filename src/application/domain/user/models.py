from pydantic import BaseModel, Field
from sqlalchemy import BigInteger, Boolean, Column, Enum, Unicode

from application.core.authority.permissions import Authority
from application.core.db import Base
from application.core.db.mixins import TimestampMixin
from application.core.fastapi.pydantic_models import ResponseBaseModel


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    password = Column(Unicode(255), nullable=False)
    email = Column(Unicode(255), nullable=False, unique=True)
    nickname = Column(Unicode(255), nullable=False, unique=True)
    authority = Column(Enum(Authority), nullable=False, default=Authority.USER)
    is_admin = Column(Boolean, default=False)


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="Access Token")
    refresh_token: str = Field(..., description="Refresh token")


class LoginRequest(BaseModel):
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")


class GetUserListResponseSchema(BaseModel):
    id: int = Field(..., description="ID")
    email: str = Field(..., description="Email")
    nickname: str = Field(..., description="Nickname")

    class Config:
        orm_mode = True


class CreateUserRequestSchema(BaseModel):
    email: str = Field(..., description="Email")
    password1: str = Field(..., description="Password1")
    password2: str = Field(..., description="Password2")
    nickname: str = Field(..., description="Nickname")


class CreateUserResponseSchema(BaseModel):
    email: str = Field(..., description="Email")
    nickname: str = Field(..., description="Nickname")

    class Config:
        orm_mode = True


class LoginResponseSchema(BaseModel):
    access_token: str = Field(..., description="Access Token")
    refresh_token: str = Field(..., description="Refresh token")


class ErrorResponse(ResponseBaseModel):
    code: str
    message: str
    data: dict | list | None
