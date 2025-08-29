from maxapi.types import (
    MessageCallback,
    CallbackButton,
)
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from ...utils import Texts, UserState
from shared_models.database import User
from bot.bot import state_machine


async def confirm_terms_of_use(callback: MessageCallback) -> None:
    # Отправляем ответ о том что сообщение пройдет модерацию
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        CallbackButton(
            text=Texts.Buttons.write_message,
            payload="write_message",
        )
    )
    
    await callback.message.answer(
        text=Texts.Messages.write_message,
        attachments=[
            keyboard.as_markup()
        ],
    )

    await state_machine.set_state(callback.callback.user.user_id, UserState.WRITE_MESSAGE)
    # Создаем пользователя
    # Используется update_or_create чтобы не было дубликатов (на всякий случай)
    await User.update_or_create(
        defaults={
            "first_name": callback.callback.user.first_name,
            "last_name": callback.callback.user.last_name,
            "username": callback.callback.user.username,
        },
        max_id=callback.callback.user.user_id,
    )

    await state_machine.set_state(callback.callback.user.user_id, UserState.WRITE_MESSAGE)


async def confirm_terms_of_use_filter(callback: MessageCallback) -> bool:
    return (
        callback.callback.payload == "confirm_terms_of_use"
        and await state_machine.get_state(callback.callback.user.user_id)
        == UserState.CONFIRM_TERMS_OF_USE
    )
