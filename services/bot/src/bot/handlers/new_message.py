from maxapi.types import MessageCallback
from ..utils import (
    Texts,
    UserState,
    Config,
    attempts_limit_reached,
    messages_limit_reached,
    messages_time_out_reached,
)
from shared_models.database import User
from bot.bot import state_machine


async def new_message(callback: MessageCallback) -> None:
    if Config.MESSAGE_COLLECTION_STOPPED:
        await callback.message.answer(
            text=Texts.Messages.message_collection_stopped,
        )
        return
    # Проверяем, достиг ли пользователь лимита попыток отправки сообщений
    # или лимита количества сообщений
    # Если достигнут, то отправляем соответствующее сообщение и выходим
    if await attempts_limit_reached(callback.from_user.user_id):
        await callback.message.answer(
            text=Texts.Messages.attempts_limit,
        )
        return
    if await messages_limit_reached(callback.from_user.user_id):
        await callback.bot.send_message(
            user_id=callback.from_user.user_id,
            text=Texts.Messages.messages_limit,
        )
        return
    if await messages_time_out_reached(callback.from_user.user_id):
        await callback.bot.send_message(
            user_id=callback.from_user.user_id,
            text=Texts.Messages.messages_time_out,
        )
        return

    if callback.payload == "new_message":
        await callback.message.answer(
            text="",
        )
    await callback.bot.send_message(
        user_id=callback.from_user.user_id,
        text=Texts.Messages.get_message,
    )

    await User.update_or_create(
        defaults={
            "first_name": callback.from_user.first_name,
            "last_name": callback.from_user.last_name,
            "username": callback.from_user.username,
        },
        max_id=callback.from_user.user_id,
    )

    await state_machine.set_state(callback.from_user.user_id, UserState.GET_MESSAGE)


def new_message_filter(callback: MessageCallback) -> bool:
    return callback.payload in ("new_message", "new_message_no_edit")
