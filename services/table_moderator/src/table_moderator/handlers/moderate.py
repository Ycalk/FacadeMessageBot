from faststream.rabbit import RabbitRouter
from logging import Logger
from table_moderator.utils import Sheet, Storage
from shared_models.messaging.queues.table_moderator import (
    table_moderator_queue,
)
from shared_models.messaging.exchanges import moderator_exchange
from shared_models.messaging import MessageInput
from faststream import Context


moderate_router = RabbitRouter()


@moderate_router.subscriber(table_moderator_queue, moderator_exchange)
async def moderate(
    message_input: MessageInput,
    logger: Logger = Context(),
    sheet: Sheet = Context(),
    storage: Storage = Context(),
):
    logger.info(f"Received message for moderation: {message_input.message.message_id}")
    await sheet.add_message(message_input.message)
    await storage.add_message(message_input.message)
    logger.info(f"Message {message_input.message.message_id} added to the sheet.")
