import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import APIKeyHeader
from media_facade.utils import Config
from shared_models.enums import ModerationResult as ModerationResultEnum
from media_facade.models import AddMessage, ModerationResult

security = APIKeyHeader(
    name="x-token",
    scheme_name="Авторизация, которая ожидается от сервиса",
    description="Передается токен в заголовке x-token.",
)


async def auth(credentials: str = Depends(security)):
    if credentials != Config.MEDIA_FACADE_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


mock_router = APIRouter(
    prefix="/api/vk",
    tags=["mocks"],
    dependencies=[Depends(auth)],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        410: {"description": "No available time"},
        430: {
            "description": f"Message text is more, than {Config.MAX_TEXT_LENGTH} symbols"
        },
        431: {
            "description": f"Message name or city is more, than {Config.MAX_NAME_AND_CITY_LENGTH} symbols"
        },
    },
)


@mock_router.post("/message", summary="Добавление нового сообщения на модерацию")
async def add_message(
    request: Request,
    message: AddMessage = Body(...),
):
    client: AsyncClient = request.app.state.httpx_mock_client
    if len(message.text) > Config.MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=430,
            detail=f"Message text is more, than {Config.MAX_TEXT_LENGTH} symbols",
        )
    if (
        len(message.name) > Config.MAX_NAME_AND_CITY_LENGTH
        or len(message.city) > Config.MAX_NAME_AND_CITY_LENGTH
    ):
        raise HTTPException(
            status_code=431,
            detail=f"Message name or city is more, than {Config.MAX_NAME_AND_CITY_LENGTH} symbols",
        )
    asyncio.create_task(mock_moderate(message, client))


async def mock_moderate(request: AddMessage, client: AsyncClient) -> None:
    await asyncio.sleep(5)
    await client.post(
        "/moderation_result",
        json=ModerationResult(
            message_id=request.id,
            result=ModerationResultEnum.APPROVED,
            ts_from=int((datetime.now() + timedelta(minutes=1)).timestamp()),
            ts_to=int((datetime.now() + timedelta(minutes=2)).timestamp()),
            reason=None,
        ).model_dump(),
    )
    await asyncio.sleep(60)
    await client.post(
        "/message_shown",
        json={"message_id": request.id},
    )
