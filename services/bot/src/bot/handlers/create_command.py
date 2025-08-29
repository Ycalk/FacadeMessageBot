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


async def create_command_handler(event: MessageCreated, bot: Bot) -> None:
    if not event.message or not event.message.from_user:
        return

    user = await User.get_or_none(max_id=event.message.from_user.user_id)
    if not user:
        return

    if Config.MESSAGE_COLLECTION_STOPPED:
        await bot.send_message(
            user_id=event.message.from_user.user_id,
            text=Texts.Messages.message_collection_stopped,
        )
        return

    # Проверяем, достиг ли пользователь лимита попыток отправки сообщений
    # или лимита количества сообщений
    # Если достигнут, то отправляем соответствующее сообщение и выходим
    if await attempts_limit_reached(event.message.from_user.user_id):
        await bot.send_message(
            user_id=event.message.from_user.user_id,
            text=Texts.Messages.attempts_limit,
        )
        return

    if await messages_limit_reached(event.message.from_user.user_id):
        await bot.send_message(
            user_id=event.message.from_user.user_id,
            text=Texts.Messages.messages_limit,
            )
        return

    if await messages_time_out_reached(event.message.from_user.user_id):
        await bot.send_message(
            user_id=event.message.from_user.user_id,
            text=Texts.Messages.messages_time_out,
        )
        return

    await bot.send_message(
        user_id=event.message.from_user.user_id,
        text=Texts.Messages.get_message,
        parse_mode=ParseMode.MARKDOWN,
    )
    await state_machine.set_state(event.message.from_user.user_id, UserState.GET_MESSAGE)


def create_command_filter(event: MessageCreated) -> bool:
    return (
        event.message is not None
        and event.message.from_user is not None
        and event.message.text is not None
        and event.message.text == "/create"
    )
