from datetime import datetime, timedelta
from typing import Literal, Union

from dependency_injector.wiring import Provide
from pydantic import Field
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String

from application.core.db import Base
from application.core.fastapi.pydantic_models import BodyBaseModel, ResponseBaseModel


class Token(Base):
    __tablename__ = "tokens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    refresh_token = Column(String, nullable=False, index=True)
    refresh_expires_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow()
    )
    is_valid = Column(Boolean, nullable=False, default=False)

    def __init__(
        self,
        user_id,
        refresh_token,
        refresh_token_expires_in: int = Provide["config.REFRESH_TOKEN_EXPIRE_SECONDS"],
    ):
        self.user_id = user_id
        self.refresh_token = refresh_token
        self.refresh_expires_at = datetime.utcnow() + timedelta(
            seconds=refresh_token_expires_in
        )
        self.is_valid = True


class RefreshTokenRequest(BodyBaseModel):
    refresh_token: str = Field(..., description="Refresh token")


class RevokeTokenRequest(BodyBaseModel):
    token: str = Field(..., description="Token")
    token_type: Literal["access_token", "refresh_token"] = Field(
        ..., description="Token"
    )


class RefreshTokenResponse(ResponseBaseModel):
    token: str = Field(...)
    refresh_token: str


class AccessTokenResponse(ResponseBaseModel):
    access_token: str = Field(...)


class RevokeTokenResponse(ResponseBaseModel):
    code: str
    message: str
    data: Union[dict | list | None]
