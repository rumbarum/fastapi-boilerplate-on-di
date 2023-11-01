import asyncio
from http import HTTPStatus

import nest_asyncio
from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI, Request

from application.api import router
from application.container import AppContainer
from application.core.enums import ResponseCode
from application.core.exceptions import CustomException
from application.core.external_service.http_client import Aiohttp
from application.core.fastapi.custom_json_response import CustomORJSONResponse
from application.domain.log.service import DatabaseLoghandler

nest_asyncio.apply()


def init_routers(app_: FastAPI) -> None:
    app_.include_router(router)


@inject
def init_listeners(
    app_: FastAPI,
    log_handler: DatabaseLoghandler = Provide["log_container.db_log_handler"],
) -> None:
    """
    Order of presence is not affecting handler.
    Only specified Exception will be handled.
    """

    @app_.exception_handler(Exception)
    async def root_exception_handler(request: Request, exc: CustomException):
        """
        Unmanaged exception will be caught here.
        """
        try:
            # fill your logging
            log_data = {
                "user_id": request.user.user_id,
                "ip": request.client.host if request.client else None,
                "port": request.client.port if request.client else None,
                "method": request.method,
                "path": request.url.path,
                "agent": dict(request.headers.items())["user-agent"],
                "response_status": HTTPStatus.INTERNAL_SERVER_ERROR,
            }
            await log_handler(log_data)
            return CustomORJSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"code": ResponseCode.UNDEFINED_ERROR, "message": exc},
            )
        except Exception as e:
            raise e

    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return CustomORJSONResponse(
            status_code=exc.http_code,
            content={"code": exc.error_code, "message": exc.message},
        )


async def create_app() -> FastAPI:
    """
    This func can be run synchronously,
    but if you declare some awaitable Resource on Container then switch to asynchronously func.
    This func support both of them.
    """
    container = AppContainer()
    container.logging.init()
    middlewares = container.middleware_list()
    config = container.config

    app_ = FastAPI(
        title=config.TITLE(),
        description=config.DESCRIPTION(),
        version=config.VERSION(),
        docs_url=None if config.ENV() == "production" else "/docs",
        redoc_url=None if config.ENV() == "production" else "/redoc",
        middleware=middlewares,
        on_startup=[],
        on_shutdown=[Aiohttp.on_shutdown],
    )

    init_routers(app_=app_)
    init_listeners(app_=app_)

    # This setting attribute is for test suit, making config accessible.
    # In normal case, use wiring.Provide["container_attr"]
    if config.ENV() != "production":
        app_.container = container  # type: ignore[attr-defined]
    return app_


app = asyncio.run(create_app())
