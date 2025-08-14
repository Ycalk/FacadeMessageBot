from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from media_facade.utils import Config
from media_facade.models import AddMessage

security = APIKeyHeader(
    name="x-token",
    scheme_name="Аутентификация, которая ожидается от сервиса",
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
        430: {"description": "Message text is more, than 80 symbols"},
        431: {"description": "Message name or city is more, than 15 symbols"},
    },
)


@mock_router.post("/message", summary="Добавление нового сообщения на модерацию")
async def add_message(
    request: AddMessage,
):
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="This endpoint is not implemented yet",
    )
