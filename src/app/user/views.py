from typing import List

from fastapi import APIRouter, Depends, Query

from core.dependencies import PermissionDependency
from core.fastapi.log_route import LogRoute
from core.helpers.cache.cache_manager import cached

from .models import (
    CreateUserRequestSchema,
    CreateUserResponseSchema,
    ErrorResponse,
    GetUserListResponseSchema,
    LoginRequest,
    LoginResponse,
)
from .service import UserService

user_router = APIRouter(route_class=LogRoute)


@user_router.get(
    "",
    response_model=List[GetUserListResponseSchema],
    response_model_exclude={"id"},
    responses={"400": {"model": ErrorResponse}},
    dependencies=[Depends(PermissionDependency([]))],
)
@cached(prefix="get_user_list", ttl=60)
async def get_user_list(
    limit: int = Query(10, description="Limit"),
    prev: int = Query(None, description="Prev ID"),
):
    return await UserService().get_user_list(limit=limit, prev=prev)


@user_router.post(
    "",
    response_model=CreateUserResponseSchema,
    responses={"400": {"model": ErrorResponse}},
)
async def create_user(request: CreateUserRequestSchema):
    await UserService().create_user(**request.dict())
    return {"email": request.email, "nickname": request.nickname}


@user_router.post(
    "/login",
    response_model=LoginResponse,
    responses={"404": {"model": ErrorResponse}},
)
async def login(request: LoginRequest):
    token = await UserService().login(email=request.email, password=request.password)
    return {"token": token.access_token, "refresh_token": token.refresh_token}
