"""Обработчик кнопки 'Написать поздравление' — переход к вводу текста поздравления."""

from core.logger import get_logger

from maxapi.types import MessageCallback
from sqlalchemy import select

from bot.instance import get_context
from bot.states import UserStates
from bot.steps import show_get_message
from bot.texts import Texts
from db.models import User
from db.session import async_session
from services.message_limits import can_send_more_messages

logger = get_logger(__name__)


async def _get_or_create_user(callback: MessageCallback) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.max_id == callback.callback.user.user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                max_id=callback.callback.user.user_id,
                first_name=getattr(callback.callback.user, "first_name", None),
                username=getattr(callback.callback.user, "username", None),
            )
            session.add(user)
            await session.commit()


async def write_greeting_handler(callback: MessageCallback) -> None:
    """Проверяет лимиты и переводит пользователя к вводу поздравления."""
    await _get_or_create_user(callback)
    user_id = callback.callback.user.user_id
    ctx = get_context(user_id)

    if not await can_send_more_messages(user_id):
        await callback.message.answer(text=Texts.Messages.messages_limit)
        return

    await show_get_message(user_id)
    await ctx.set_state(UserStates.get_message)
