from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from .models import AccessTokenResponse, RefreshTokenRequest
from .service import TokenService

auth_router = APIRouter()


@auth_router.post(
    "/refresh",
    response_model=AccessTokenResponse,
)
@inject
async def refresh_token(
    request: RefreshTokenRequest,
    token_service: TokenService = Depends(Provide["token_container.token_service"]),
):
    new_access_token = await token_service.refresh_access_token(
        refresh_token=request.refresh_token
    )
    return {"access_token": new_access_token}
