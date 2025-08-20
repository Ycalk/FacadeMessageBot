from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from shared_models.messaging import Message, MessageInput
from shared_models.messaging import ModerationResult as ModerationResultSharedModel
from shared_models.messaging import (
    bot_exchange,
    bot_moderate_response_queue,
    vision_exchange,
    vision_notification_queue,
)
from shared_models.enums import ModerationResult as ModerationResultEnum
from shared_models.enums import ModeratorType
from shared_models.database import Message as MessageDB
from media_facade.utils import Config
from media_facade.models import ModerationResult
from faststream.rabbit import RabbitBroker
from datetime import datetime


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
    request: Request,
    message_id: int = Body(..., embed=True, description="ID сообщения"),
):
    broker: RabbitBroker = request.state.broker
    message = await MessageDB.get_or_none(id=message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    returned_message = Message(
        message_id=message.id,
        text=message.text,
        name=message.name,
        city=message.city,
        send_photo=message.send_photo,
    )
    await broker.publish(
        MessageInput(message=returned_message),
        vision_notification_queue,
        vision_exchange,
    )
    return returned_message


@webhooks_router.post(
    "/moderation_result", summary="Результат модерации", response_model=Message
)
async def moderation_result(request: Request, message: ModerationResult):
    message_model = await MessageDB.get_or_none(id=message.message_id)
    broker: RabbitBroker = request.state.broker

    if not message_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    if message.result == ModerationResultEnum.APPROVED:
        if message.ts_to is None or message.ts_from is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ts_to and ts_from must be provided for approved messages",
            )
        message_model.show_time_start = datetime.fromtimestamp(
            message.ts_from, tz=Config.TIME_ZONE
        )
        message_model.show_time_end = datetime.fromtimestamp(
            message.ts_to, tz=Config.TIME_ZONE
        )
        await message_model.save()

    message_shared_model = Message(
        message_id=message_model.id,
        text=message_model.text,
        name=message_model.name,
        city=message_model.city,
        send_photo=message_model.send_photo,
    )

    await broker.publish(
        ModerationResultSharedModel(
            message=message_shared_model,
            source=ModeratorType.MEDIA_FACADE,
            result=message.result,
            reason=message.reason,
        ),
        bot_moderate_response_queue,
        bot_exchange,
    )

    return message_shared_model
