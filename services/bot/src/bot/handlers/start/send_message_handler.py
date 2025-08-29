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
from shared_models.database import User


async def send_message_handler(callback: MessageCallback) -> None:
    # Создаем пользователя если он новый
    await User.update_or_create(
        defaults={
            "first_name": callback.callback.user.first_name,
            "last_name": callback.callback.user.last_name,
            "username": callback.callback.user.username,
        },
        max_id=callback.callback.user.user_id,
    )
    
    # Проверяем глобальную блокировку сбора сообщений
    if Config.MESSAGE_COLLECTION_STOPPED:
        await callback.message.answer(
            text=Texts.Messages.message_collection_stopped,
        )
        return

    # Проверяем лимиты пользователя
    if await attempts_limit_reached(callback.callback.user.user_id):
        await callback.message.answer(
            text=Texts.Messages.attempts_limit,
        )
        return
        
    if await messages_limit_reached(callback.callback.user.user_id):
        await callback.message.answer(
            text=Texts.Messages.messages_limit,
        )
        return
        
    if await messages_time_out_reached(callback.callback.user.user_id):
        await callback.message.answer(
            text=Texts.Messages.messages_time_out,
        )
        return

    # Все проверки пройдены - просим ввести сообщение
    await callback.message.answer(
        text=Texts.Messages.get_message,
    )

    await state_machine.set_state(callback.callback.user.user_id, UserState.GET_MESSAGE)


async def send_message_filter(callback: MessageCallback) -> bool:
    return (
        callback.payload == "send_message"
        and await state_machine.get_state(callback.callback.user.user_id)
        == UserState.SEND_MESSAGE
    )
