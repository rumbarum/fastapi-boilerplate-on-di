from fastapi import APIRouter, Depends, Response

from application.core.dependencies import PermissionDependency
from application.core.fastapi.log_route import LogRoute
from application.core.authority.permissions import AllowAll

home_router = APIRouter(route_class=LogRoute)


@home_router.get("/health", dependencies=[Depends(PermissionDependency([AllowAll]))])
async def home():
    return Response(status_code=200)
