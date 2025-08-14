from shared_models.messaging import MessageInput, ModerationResult
from shared_models.enums import ModerationResult as ModerationResultEnum
from shared_models.enums import ModeratorType
from shared_models.messaging.exchanges import moderator_exchange, dlx_exchange
from shared_models.messaging.queues import (
    facade_message_moderator_queue,
    facade_message_moderator_dlx_queue,
)
from faststream.rabbit import RabbitRouter
from logging import Logger
from media_facade.models import AddMessage
from faststream.rabbit.fastapi import Context
from httpx import AsyncClient

moderate_router = RabbitRouter()

dlx = moderate_router.publisher(facade_message_moderator_dlx_queue, dlx_exchange)


@moderate_router.subscriber(facade_message_moderator_queue, moderator_exchange)
async def moderate(
    message_input: MessageInput,
    logger: Logger = Context("logger"),
    httpx_client: AsyncClient = Context("httpx_client"),
) -> None:
    logger.info(f"Received message {message_input.message.message_id} for moderation.")
    response = await httpx_client.post(
        "/message",
        json=AddMessage.from_message(message_input.message).model_dump(),
    )
    if response.status_code != 200:
        logger.error(
            f"Failed to moderate message {message_input.message.message_id}: {response.text}"
        )
        await dlx.publish(
            ModerationResult(
                message=message_input.message,
                source=ModeratorType.MEDIA_FACADE,
                result=ModerationResultEnum.REJECTED,
                reason=f"Failed to moderate message {message_input.message.message_id}: {response.text}",
            )
        )
    else:
        logger.info(f"Message {message_input.message.message_id} send to moderation.")
