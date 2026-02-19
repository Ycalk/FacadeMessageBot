"""Обработчик кнопки 'Редактировать' — возврат к вводу текста поздравления."""

from core.logger import get_logger

from maxapi.types import MessageCallback

from bot.instance import get_context
from bot.states import UserStates
from bot.steps import show_get_message
from bot.handlers.wrong_step import reply_wrong_step_for_callback

logger = get_logger(__name__)


async def edit_greeting_handler(callback: MessageCallback) -> None:
    """Возвращает пользователя к вводу текста поздравления."""
    user_id = callback.callback.user.user_id
    ctx = get_context(user_id)
    current_state = await ctx.get_state()

    if current_state != str(UserStates.preview):
        await reply_wrong_step_for_callback(callback)
        return

    await show_get_message(user_id)
    await ctx.set_state(UserStates.get_message)
