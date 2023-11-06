from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from application.core.dependencies import PermissionDependency
from application.core.fastapi.log_route import LogRoute
from application.core.helpers.cache.cache_manager import cached

from .models import (
    CreateUserIn,
    CreateUserOut,
    ErrorOut,
    GetUserListOut,
    LoginRequest,
    LoginResponse,
)
from .service import UserService

user_router = APIRouter(route_class=LogRoute)


@user_router.get(
    "",
    response_model=List[GetUserListOut],
    response_model_exclude={"id"},
    responses={"400": {"model": ErrorOut}},
    dependencies=[Depends(PermissionDependency([]))],
)
@cached(prefix="get_user_list", ttl=60)
@inject
async def get_user_list(
    limit: int = Query(10, description="Limit"),
    prev: int = Query(None, description="Prev ID"),
    user_service: UserService = Depends(Provide["user_container.user_service"]),
):
    return await user_service.get_user_list(limit=limit, prev=prev)


@user_router.post(
    "",
    response_model=CreateUserOut,
    responses={"400": {"model": ErrorOut}},
)
@inject
async def create_user(
    request: CreateUserIn,
    user_service: UserService = Depends(Provide["user_container.user_service"]),
):
    await user_service.create_user(**request.dict())
    return {"email": request.email, "nickname": request.nickname}


@user_router.post(
    "/login",
    response_model=LoginResponse,
    responses={"404": {"model": ErrorOut}},
)
@inject
async def login(
    request: LoginRequest,
    user_service: UserService = Depends(Provide["user_container.user_service"]),
):
    token = await user_service.login(email=request.email, password=request.password)
    return {"token": token.access_token, "refresh_token": token.refresh_token}
