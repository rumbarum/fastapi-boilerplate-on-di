from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from application.core.dependencies.permission import PermissionDependency
from application.core.enums import ResponseCode
from application.core.fastapi.custom_json_response import CustomORJSONResponse
from application.core.fastapi.log_route import LogRoute

from .models import YourResponseModel
from .service import YourService

# register below to domain.api.py
your_router = APIRouter(route_class=LogRoute)


@your_router.get(
    "/your_path",
    dependencies=[Depends(PermissionDependency([]))],
    response_model=YourResponseModel,
)
@inject
async def your_endpoint(
    request: Request,
    your_service: YourService = Depends(Provide["your_domain_container.your_service"]),
):
    """
    your_endpoint
    """
    # your code here
    return CustomORJSONResponse(
        status_code=HTTPStatus.OK,
        content={"code": ResponseCode.OK, "message": "success"},
    )
