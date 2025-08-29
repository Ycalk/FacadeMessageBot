from maxapi.types import MessageCallback
from bot.bot import state_machine
from bot.utils import (
    Texts,
    UserState,
    Config,
    attempts_limit_reached,
    messages_limit_reached,
    messages_time_out_reached,
)


async def write_message_handler(callback: MessageCallback) -> None:
    # Реакция на сообщение о том, что сообщение пройдет модерацию
    await callback.message.answer(
        text=Texts.Messages.write_message,
    )

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

    # Начинаем сбор послания пользователя
    # Сначала спрашиваем сообщение, которое пользователь хочет отправить
    await callback.bot.send_message(
        user_id=callback.from_user.user_id,
        text=Texts.Messages.get_message,
    )
    await state_machine.set_state(callback.from_user.user_id, UserState.GET_MESSAGE)


async def write_message_filter(callback: MessageCallback) -> bool:
    return (
        callback.payload == "write_message"
        and await state_machine.get_state(callback.from_user.user_id)
        == UserState.WRITE_MESSAGE
    )
