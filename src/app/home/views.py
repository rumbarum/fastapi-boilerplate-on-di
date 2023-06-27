from fastapi import APIRouter, Depends, Response

from app.auth.permissions import AllowAll
from core.dependencies import PermissionDependency
from core.fastapi.log_route import LogRoute

home_router = APIRouter(route_class=LogRoute)


@home_router.get("/health", dependencies=[Depends(PermissionDependency([AllowAll]))])
async def home():
    return Response(status_code=200)
