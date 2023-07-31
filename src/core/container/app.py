from dependency_injector import containers, providers
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.auth.container import AuthContainer
from app.log.container import LogContainer
from app.user.container import UserContainer
from core.db.session_maker import RoutingSession, get_session_context
from core.external_service.auth_client import AuthClient
from core.helpers.cache import CacheManager, CustomKeyMaker, RedisBackend
from core.helpers.logging import init_logger
from core.middlewares import (
    AuthenticationMiddleware,
    ExternalAuthBackend,
    on_auth_error,
)
from core.middlewares.sqlalchemy import SQLAlchemyMiddleware
from core.utils.http_client import Aiohttp

from .config import config_container


class AppContainer(containers.DeclarativeContainer):
    # config loaded from pydantic model
    config = config_container.config

    # dependency injector coverage
    wiring_config = containers.WiringConfiguration(
        packages=["app", "core", "api"],
        modules=[__name__],
    )
    logging = providers.Resource(init_logger, env=config.ENV)

    # async client
    async_http_client = providers.Callable(
        Aiohttp.get_aiohttp_client,
        client_timeout=config.CLIENT_TIME_OUT,
        limit_per_host=config.SIZE_POOL_AIOHTTP,
    )

    auth_client = providers.Singleton(
        AuthClient,
        auth_base_url=config.AUTH_BASE_URL,
        client_id=config.AUTH_CLIENT_ID,
        client_secret=config.AUTH_CLIENT_SECRET,
        refresh_token_key=config.AUTH_REFRESH_TOKEN_KEY,
        scope=config.AUTH_SCOPE,
        session=async_http_client,
        ssl=True if config.ENV == "production" else False,
    )

    # middleware
    cors_middleware = providers.Factory(
        Middleware,
        CORSMiddleware,
        allow_origins=config.ALLOW_ORIGINS,
        allow_credentials=config.ALLOW_CREDENTIALS,
        allow_methods=config.ALLOW_METHODS,
        allow_headers=config.ALLOW_HEADERS,
    )
    auth_backend = providers.Singleton(
        # auth_client is injected on AstAuthBackend declaration
        ExternalAuthBackend
    )
    auth_middleware = providers.Singleton(
        Middleware,
        AuthenticationMiddleware,
        backend=auth_backend,
        on_error=on_auth_error,
    )
    sqlalchemy_middleware = providers.Factory(Middleware, SQLAlchemyMiddleware)
    middleware_list = providers.List(
        cors_middleware,
        auth_middleware,
        sqlalchemy_middleware,
    )

    # redis
    redis_backend = providers.Factory(RedisBackend)
    redis_key_maker = providers.Factory(CustomKeyMaker)
    redis = providers.Singleton(
        Redis.from_url,
        # this value should be called when declared. If not, repr(config.value) will be injected.
        url=f"redis://{config.REDIS_HOST()}:{config.REDIS_PORT()}",
    )
    cache_manager = providers.Singleton(
        CacheManager, backend=redis_backend, key_maker=redis_key_maker
    )

    # session
    writer_engine = providers.Factory(
        create_async_engine, config.WRITER_DB_URL, pool_recycle=3600
    )
    reader_engine = providers.Factory(
        create_async_engine, config.READER_DB_URL, pool_recycle=3600
    )

    async_session_factory = providers.Factory(
        sessionmaker,
        class_=AsyncSession,
        sync_session_class=RoutingSession,
    )
    session = providers.ThreadSafeSingleton(
        async_scoped_session,
        session_factory=async_session_factory,
        scopefunc=get_session_context,
    )

    # app/.../container
    user_container = providers.Container(UserContainer)
    auth_container = providers.Container(AuthContainer)
    log_container = providers.Container(LogContainer)
