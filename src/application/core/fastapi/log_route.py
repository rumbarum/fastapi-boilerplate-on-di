from typing import Callable

from dependency_injector.wiring import Provide, inject
from fastapi import BackgroundTasks, Request, Response
from fastapi.routing import APIRoute


class LogRoute(APIRoute):
    @inject
    def get_route_handler(
        self, log_handler=Provide["log_container.db_log_handler"]
    ) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:

            response: Response = await original_route_handler(request)

            log_data = {
                "user_id": request.user.user_id,
                "ip": request.client.host if request.client else None,
                "port": request.client.port if request.client else None,
                "method": request.method,
                "path": request.url.path,
                "agent": dict(request.headers.items())["user-agent"],
                "response_status": response.status_code,
            }

            pre_background = response.background
            response.background = BackgroundTasks()
            if pre_background:
                response.background = BackgroundTasks([pre_background])
            response.background.add_task(func=log_handler, data=log_data)
            return response

        return custom_route_handler
