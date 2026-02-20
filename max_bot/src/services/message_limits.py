"""Проверка лимитов отправки поздравлений."""

from sqlalchemy import select, func

from core.config import Config
from db.models import Message, User
from db.session import async_session


async def can_send_more_messages(max_user_id: int, additional_messages: int = 0) -> bool:
    """
    Проверяет, может ли пользователь отправить ещё сообщения.

    additional_messages:
    - 0: проверить возможность отправить прямо сейчас;
    - 1: проверить, останется ли возможность после текущей отправки.
    """
    if max_user_id in Config.unlimited_users_list:
        return True
    if Config.MAXIMUM_MESSAGES_PER_USER <= 0:
        return True

    async with async_session() as session:
        user_result = await session.execute(
            select(User).where(User.max_id == max_user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            return True

        count_result = await session.execute(
            select(func.count(Message.id)).where(Message.user_id == user.id)
        )
        count = count_result.scalar() or 0
        return (count + additional_messages) < Config.MAXIMUM_MESSAGES_PER_USER
