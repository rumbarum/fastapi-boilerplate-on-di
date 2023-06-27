import os
from typing import Any, Optional

from pydantic import BaseConfig, BaseSettings, Field


class Settings(BaseSettings):
    # Basic Settings
    TITLE: str
    DESCRIPTION: str
    VERSION: str
    ENV: str
    DEBUG: bool
    APP_HOST: str
    APP_PORT: int
    APP_DOMAIN: str
    WRITER_DB_URL: str
    READER_DB_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "SHA256"
    SENTRY_SDN: Optional[str] = None
    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: str
    REDIS_HOST: str
    REDIS_PORT: int
    JWT_EXPIRE_SECONDS: int = 3600
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 86400

    # Aio HTTP config
    CLIENT_TIME_OUT: int
    SIZE_POOL_AIOHTTP: int

    # External API Settings
    AUTH_BASE_URL: str
    AUTH_CLIENT_ID: str
    AUTH_CLIENT_SECRET: str
    AUTH_REFRESH_TOKEN_KEY: str
    AUTH_SCOPE: list[str] = Field(..., env="AUTH_SCOPE")

    # CORS Settings
    ALLOW_ORIGINS: list[str] = Field(..., env="ALLOW_ORIGINS")
    ALLOW_CREDENTIALS: bool
    ALLOW_METHODS: list[str] = Field(..., env="ALLOW_METHODS")
    ALLOW_HEADERS: list[str] = Field(..., env="ALLOW_HEADERS")

    class Config(BaseConfig):
        env_file = os.getenv("ENV_FILE", ".env.local")
        env_file_encoding = "utf-8"

        comma_separated_key = [
            "AUTH_SCOPE",
            "ALLOW_ORIGINS",
            "ALLOW_METHODS",
            "ALLOW_HEADERS",
        ]

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            """comma separated string to list"""
            if field_name in cls.comma_separated_key:
                return [scope for scope in raw_val.split(",")]
            return cls.json_loads(raw_val)
