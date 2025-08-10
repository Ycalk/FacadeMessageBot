from logging import Logger
from tortoise.transactions import in_transaction
from faststream.rabbit import RabbitRouter
from shared_models.messaging import (
    bot_exchange,
    bot_moderate_response_queue,
    ModerationResult,
)
from aiomax import Bot
from faststream import Context
from shared_models.enums import ModeratorType, MessageState
from shared_models.enums import ModerationResult as ModerationResultEnum
from aiomax.methods import SendMessage
from aiomax.types import TextFormat
from shared_models.database import Message, ModerationLog
from bot.utils import Texts


moderation_result_router = RabbitRouter()


@moderation_result_router.subscriber(bot_moderate_response_queue, bot_exchange)
async def moderation_result_handler(
    moderation_result: ModerationResult,
    logger: Logger = Context(),
    bot: Bot = Context(),
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
                if message.state == MessageState.PENDING_AUTO_MODERATION:
                    message.state = MessageState.PENDING_MANUAL_MODERATION
                    await message.save()

                    await ModerationLog.create(
                        message=message,
                        source=moderation_result.source,
                        result=moderation_result.result,
                        reason=moderation_result.reason,
                    )

                    await bot(
                        SendMessage(
                            user_id=message.user.max_id,
                            text=Texts.Messages.auto_moderation_completed,
                            text_format=TextFormat.MARKDOWN,
                        )
                    )
                else:
                    logger.warning(
                        f"Message {message.id} is not in pending auto-moderation state. Current state: {message.state}"
                    )

            elif moderation_result.source == ModeratorType.MANUAL:
                if message.state == MessageState.PENDING_MANUAL_MODERATION:
                    message.state = MessageState.PENDING_MEDIA_FACADE_MODERATION
                    await message.save()

                    await ModerationLog.create(
                        message=message,
                        source=moderation_result.source,
                        result=moderation_result.result,
                        reason=moderation_result.reason,
                    )

                    await bot(
                        SendMessage(
                            user_id=message.user.max_id,
                            text=Texts.Messages.manual_moderation_completed,
                            text_format=TextFormat.MARKDOWN,
                        )
                    )
                else:
                    logger.warning(
                        f"Message {message.id} is not in pending manual-moderation state. Current state: {message.state}"
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
