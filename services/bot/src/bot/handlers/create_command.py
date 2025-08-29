import logging
from maxapi.types import MessageCreated
from maxapi.enums.parse_mode import ParseMode
from maxapi import Bot
from bot.utils import (
    Texts,
    Config,
    UserState,
    attempts_limit_reached,
    messages_limit_reached,
    messages_time_out_reached,
)
from bot.bot import state_machine
from shared_models.database import User

logger = logging.getLogger(__name__)


async def create_command_handler(event: MessageCreated, bot: Bot) -> None:
    if not event.message or not event.message.sender:
        logger.debug("create_command_handler: Нет сообщения или отправителя")
        return
        
    logger.debug(f"create_command_handler: Обработка команды create от пользователя {event.message.sender.user_id}")

    user = await User.get_or_create(max_id=event.message.sender.user_id)
    if not user:
        logger.debug(f"create_command_handler: Пользователь {event.message.sender.user_id} не найден в БД")
        return

    if Config.MESSAGE_COLLECTION_STOPPED:
        logger.debug(f"create_command_handler: Сбор сообщений остановлен для пользователя {event.message.sender.user_id}")
        await bot.send_message(
            user_id=event.message.sender.user_id,
            text=Texts.Messages.message_collection_stopped,
        )
        return

    # Проверяем, достиг ли пользователь лимита попыток отправки сообщений
    # или лимита количества сообщений
    # Если достигнут, то отправляем соответствующее сообщение и выходим
    if await attempts_limit_reached(event.message.sender.user_id):
        logger.debug(f"create_command_handler: Достигнут лимит попыток для пользователя {event.message.sender.user_id}")
        await bot.send_message(
            user_id=event.message.sender.user_id,
            text=Texts.Messages.attempts_limit,
        )
        return

    if await messages_limit_reached(event.message.sender.user_id):
        logger.debug(f"create_command_handler: Достигнут лимит сообщений для пользователя {event.message.sender.user_id}")
        await bot.send_message(
            user_id=event.message.sender.user_id,
            text=Texts.Messages.messages_limit,
            )
        return

    if await messages_time_out_reached(event.message.sender.user_id):
        logger.debug(f"create_command_handler: Не истек таймаут для пользователя {event.message.sender.user_id}")
        await bot.send_message(
            user_id=event.message.sender.user_id,
            text=Texts.Messages.messages_time_out,
        )
        return

    logger.debug(f"create_command_handler: Переходим к получению сообщения для пользователя {event.message.sender.user_id}")
    await bot.send_message(
        user_id=event.message.sender.user_id,
        text=Texts.Messages.get_message,
        parse_mode=ParseMode.MARKDOWN,
    )
    await state_machine.set_state(event.message.sender.user_id, UserState.GET_MESSAGE)


def create_command_filter(event: MessageCreated) -> bool:
    return (
        event.message is not None
        and event.message.sender is not None
        and event.message.body.text is not None
        and event.message.body.text == "/create"
    )
