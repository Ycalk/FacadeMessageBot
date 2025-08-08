from faststream.rabbit import RabbitRouter
from logging import Logger
from aiogram import Bot
from shared_models.messaging.queues.auto_moderator import auto_moderator_queue
from shared_models.messaging.queues.bot import bot_moderate_response_queue
from shared_models.messaging.exchanges import moderator_exchange, bot_exchange
from shared_models.messaging import MessageInput, ModerationResult
from shared_models.enums import ModeratorType
from shared_models.enums import ModerationResult as ModerationResultEnum
from manual_moderator.utils import BotData, Moderator, Admin, Texts
from faststream import Context


moderate_router = RabbitRouter()

bot_moderate_response = moderate_router.publisher(
    bot_moderate_response_queue, bot_exchange
)


@moderate_router.subscriber(auto_moderator_queue, moderator_exchange)
async def moderate(
    message_input: MessageInput, logger: Logger = Context(), bot: Bot = Context()
):
    logger.info(f"Received message {message_input.message.message_id} for moderation.")
    if await BotData.is_auto_approve_enabled():
        logger.info("Auto-approve is enabled, returning value without moderation.")
        await bot_moderate_response.publish(
            ModerationResult(
                message=message_input.message,
                source=ModeratorType.MANUAL,
                result=ModerationResultEnum.APPROVED,
                reason="Auto-approve is enabled.",
            )
        )

    moderators = [
        moderator for moderator in await Moderator.all() if moderator.is_active
    ]
    if len(moderators) == 0:
        admins = await Admin.all()
        logger.warning("No moderators found, returning value without moderation.")
        await bot_moderate_response.publish(
            ModerationResult(
                message=message_input.message,
                source=ModeratorType.MANUAL,
                result=ModerationResultEnum.APPROVED,
                reason="No moderators available.",
            )
        )
        for admin in admins:
            await bot.send_message(
                chat_id=admin.telegram_id,
                text=Texts.Messages.no_moderators_available,
            )
        return

    await BotData.add_message_to_processing_queue(message_input.message)
