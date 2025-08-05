from logging import Logger
from tortoise.transactions import in_transaction
from faststream.rabbit import RabbitRouter
from shared_models.messaging import (
    bot_exchange,
    bot_moderate_response_queue,
    ModerationResult,
)
from faststream import Context
from shared_models.enums import ModeratorType, MessageState
from shared_models.enums import ModerationResult as ModerationResultEnum
from aiomax.methods import SendMessage
from aiomax.types import TextFormat
from shared_models.database import Message
from bot.bot import bot
from bot.utils import Texts


moderation_result_router = RabbitRouter()


@moderation_result_router.subscriber(bot_moderate_response_queue, bot_exchange)
async def moderation_result_handler(
    moderation_result: ModerationResult, logger: Logger = Context()
) -> None:
    async with in_transaction():
        message = await Message.get_or_none(
            id=moderation_result.message.message_id
        ).prefetch_related("user")
        if not message:
            logger.warning(
                f"Message with ID {moderation_result.message.message_id} not found."
            )
            return
        if moderation_result.result == ModerationResultEnum.APPROVED:
            if moderation_result.source == ModeratorType.AUTO:
                message.state = MessageState.PENDING_MANUAL_MODERATION
                await message.save()
                await bot(
                    SendMessage(
                        user_id=message.user.max_id,
                        text=Texts.Messages.auto_moderation_completed,
                        text_format=TextFormat.MARKDOWN,
                    )
                )
        else:
            message.state = MessageState.REJECTED
            await message.save()
            await bot(
                SendMessage(
                    user_id=message.user.max_id,
                    text=Texts.Messages.moderation_failed,
                    text_format=TextFormat.MARKDOWN,
                )
            )
