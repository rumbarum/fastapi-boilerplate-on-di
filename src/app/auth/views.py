from fastapi import APIRouter

from .models import AccessTokenResponse, RefreshTokenRequest
from .service import TokenService

auth_router = APIRouter()


@auth_router.post(
    "/refresh",
    response_model=AccessTokenResponse,
)
async def refresh_token(request: RefreshTokenRequest):
    new_access_token = await TokenService().refresh_access_token(
        refresh_token=request.refresh_token
    )
    return {"access_token": new_access_token}
