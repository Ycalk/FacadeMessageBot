from logging import Logger
from tortoise.transactions import in_transaction
from faststream.rabbit import RabbitRouter
from shared_models.messaging import (
    bot_exchange,
    bot_moderate_response_queue,
    ModerationResult,
)
from maxapi import Bot
from maxapi.types.attachments.buttons import CallbackButton, LinkButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.enums.parse_mode import ParseMode
from faststream import Context
from shared_models.enums import ModeratorType, MessageState
from shared_models.enums import ModerationResult as ModerationResultEnum
from shared_models.database import Message, ModerationLog
from bot.utils import Texts, Config
from babel.dates import format_datetime


moderation_result_router = RabbitRouter()


async def send_user_message(bot: Bot, user_id: int, text: str, attachments=None):
    """Отправка сообщения пользователю."""
    await bot.send_message(
        user_id=user_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        attachments=attachments or [],
    )


async def log_and_cancel(logger: Logger, message: Message, bot: Bot, reason: str):
    """Логирует проблему, переводит сообщение в CANCELED и уведомляет пользователя."""
    logger.warning(reason)
    message.state = MessageState.CANCELED
    await message.save()
    await send_user_message(
        bot, message.user.max_id, Texts.Messages.some_thing_went_wrong
    )


async def create_log(message: Message, moderation_result: ModerationResult):
    """Создание записи в журнале модерации."""
    await ModerationLog.create(
        message=message,
        source=moderation_result.source,
        result=moderation_result.result,
        reason=moderation_result.reason,
    )


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

        if moderation_result.result != ModerationResultEnum.APPROVED:
            message.state = MessageState.REJECTED
            await message.save()
            rejection_text = (
                Texts.Messages.auto_moderation_rejected
                if moderation_result.source == ModeratorType.AUTO
                else Texts.Messages.manual_moderation_rejected
            )
            attachments = None
            if moderation_result.source == ModeratorType.AUTO:
                keyboard = InlineKeyboardBuilder()
                keyboard.add(
                    LinkButton(
                        text=Texts.Buttons.terms_of_use,
                        url=Config.TERMS_OF_USE_URL,
                    )
                )
                attachments = [keyboard.as_markup()]
            await send_user_message(
                bot, message.user.max_id, rejection_text, attachments
            )
            return

        # === APPROVED case ===
        source, state = moderation_result.source, message.state

        if source == ModeratorType.AUTO:
            if state == MessageState.PENDING_AUTO_MODERATION:
                message.state = MessageState.PENDING_MANUAL_MODERATION
                await message.save()
                await create_log(message, moderation_result)
                # Uncomment if you want to notify users about auto moderation completion
                # await send_user_message(
                #     bot, message.user.max_id, Texts.Messages.auto_moderation_completed
                # )
            else:
                await log_and_cancel(
                    logger,
                    message,
                    bot,
                    f"Message {message.id} is not in pending auto-moderation state. Current state: {state}",
                )

        elif source == ModeratorType.MANUAL:
            if state in (
                MessageState.PENDING_MANUAL_MODERATION,
                MessageState.PENDING_AUTO_MODERATION,
            ):
                message.state = MessageState.PENDING_TABLE_MODERATION
                await message.save()
                await create_log(message, moderation_result)
                # Uncomment if you want to notify users about manual moderation completion
                # await send_user_message(
                #     bot, message.user.max_id, Texts.Messages.manual_moderation_completed
                # )
            else:
                await log_and_cancel(
                    logger,
                    message,
                    bot,
                    f"Message {message.id} is not in pending manual-moderation state. Current state: {state}",
                )

        elif source == ModeratorType.TABLE:
            if state in (
                MessageState.PENDING_TABLE_MODERATION,
                MessageState.PENDING_MANUAL_MODERATION,
            ):
                message.state = MessageState.PENDING_MEDIA_FACADE_MODERATION
                await message.save()
                await create_log(message, moderation_result)
                # Uncomment if you want to notify users about table moderation completion
                # await send_user_message(
                #     bot, message.user.max_id, Texts.Messages.manual_moderation_completed
                # )
            else:
                await log_and_cancel(
                    logger,
                    message,
                    bot,
                    f"Message {message.id} is not in pending manual-moderation state. Current state: {state}",
                )

        elif source == ModeratorType.MEDIA_FACADE:
            if state in (
                MessageState.PENDING_MEDIA_FACADE_MODERATION,
                MessageState.PENDING_MANUAL_MODERATION,
                MessageState.APPROVED,
            ):
                message.state = MessageState.APPROVED
                await message.save()
                await create_log(message, moderation_result)

                if not message.show_time_start or not message.show_time_end:
                    await log_and_cancel(
                        logger,
                        message,
                        bot,
                        f"Message {message.id} has no show time set. Canceled.",
                    )
                    return

                start_local = message.show_time_start.astimezone(Config.TIME_ZONE)
                end_local = message.show_time_end.astimezone(Config.TIME_ZONE)

                show_at = (
                    f"{format_datetime(start_local, 'd MMMM, HH:mm', locale='ru')} до "
                    f"{format_datetime(end_local, 'HH:mm', locale='ru')}"
                )

                keyboard = InlineKeyboardBuilder()
                keyboard.add(
                    CallbackButton(
                        text=Texts.Buttons.accept_get_photo,
                        payload=f"accept_get_photo:{message.id}",
                    )
                )
                keyboard.add(
                    CallbackButton(
                        text=Texts.Buttons.reject_get_photo,
                        payload=f"reject_get_photo:{message.id}",
                    ),
                )
                await send_user_message(
                    bot,
                    message.user.max_id,
                    Texts.Messages.moderation_done,
                    attachments=[],
                )
                await send_user_message(
                    bot,
                    message.user.max_id,
                    Texts.Messages.moderation_completed.format(show_at=show_at),
                    attachments=[keyboard.as_markup()],
                )
            else:
                await log_and_cancel(
                    logger,
                    message,
                    bot,
                    f"Message {message.id} is not in pending media-facade-moderation state. Current state: {state}",
                )

        else:
            await log_and_cancel(
                logger, message, bot, f"Unknown moderation source: {source}"
            )
