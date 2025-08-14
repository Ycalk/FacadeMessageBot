from shared_models.messaging import MessageInput
from shared_models.messaging.exchanges import moderator_exchange
from shared_models.messaging.queues import facade_message_moderator_queue
from faststream.rabbit import RabbitRouter
from logging import Logger
from faststream.rabbit.fastapi import Context
from httpx import AsyncClient

moderate_router = RabbitRouter()


@moderate_router.subscriber(facade_message_moderator_queue, moderator_exchange)
async def moderate(
    message_input: MessageInput,
    logger: Logger = Context("logger"),
    httpx_client: AsyncClient = Context("httpx_client"),
) -> None:
    logger.info(f"Received message {message_input.message.message_id} for moderation.")
