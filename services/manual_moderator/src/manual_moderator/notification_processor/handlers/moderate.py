from faststream.rabbit import RabbitRouter
from logging import Logger
from aiogram import Bot
from shared_models.messaging.queues.manual_moderator import manual_moderator_queue
from shared_models.messaging.exchanges import moderator_exchange
from shared_models.messaging import MessageInput
from manual_moderator.utils import BotData
from faststream import Context


moderate_router = RabbitRouter()


@moderate_router.subscriber(manual_moderator_queue, moderator_exchange)
async def moderate(
    message_input: MessageInput, logger: Logger = Context(), bot: Bot = Context()
):
    logger.info(f"Received message {message_input.message.message_id} for moderation.")
    await BotData.add_message_to_processing_queue(message_input.message)
