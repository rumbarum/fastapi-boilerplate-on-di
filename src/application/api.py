from fastapi import APIRouter

from application.core.fastapi.custom_json_response import CustomORJSONResponse
from application.core.fastapi.pydantic_models import ResponseBaseModel
from application.domain.auth.views import auth_router
from application.domain.home.views import home_router
from application.domain.user.views import user_router as user_v1_router


class ErrorResponse(ResponseBaseModel):
    code: str
    message: str
    data: dict | list | None


router = APIRouter(
    default_response_class=CustomORJSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

# root path router
router.include_router(home_router, tags=["Home"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])

# v1 router
v1_router = APIRouter(prefix="/api/v1", tags=["API_V1"])
v1_router.include_router(user_v1_router, prefix="/users", tags=["User"])

router.include_router(v1_router)

# v2 router
v2_router = APIRouter(prefix="/api/v2", tags=["API_V2"])

# attach v2 related routers to v2_router
# v2_router.include_router(some_v2_router, prefix="/some_path", tags=["Some_tag"])
router.include_router(v2_router)
