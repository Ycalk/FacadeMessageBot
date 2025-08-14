from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from shared_models.messaging import Message
from media_facade.utils import Config
from media_facade.models import ModerationResult


security = HTTPBearer(
    scheme_name="Основная авторизация",
    description="Для использования API необходимо передать токен в заголовке Authorization в формате 'Bearer <токен>'.",
)


async def auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != Config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


webhooks_router = APIRouter(
    prefix="/api/v1/webhook",
    tags=["webhooks"],
    dependencies=[Depends(auth)],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Message not Found"},
    },
)


@webhooks_router.post(
    "/message_shown", summary="Сообщение показано", response_model=Message
)
async def message_shown(
    message_id: int = Body(..., embed=True, description="ID сообщения"),
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="This endpoint is not implemented yet",
    )


@webhooks_router.post(
    "/moderation_result", summary="Результат модерации", response_model=Message
)
async def moderation_result(message: ModerationResult):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="This endpoint is not implemented yet",
    )
