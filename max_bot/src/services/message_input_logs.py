"""Логирование сообщений пользователя на шаге ввода поздравления."""

from sqlalchemy import select

from core.logger import get_logger
from db.models import MessageInputLog, User
from db.session import async_session

logger = get_logger(__name__)


async def log_get_message_input(
    user_max_id: int,
    text: str,
) -> None:
    """Сохраняет сообщение пользователя, введённое на шаге get_message."""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.max_id == user_max_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                user = User(
                    max_id=user_max_id,
                )
                session.add(user)
                await session.flush()

            session.add(
                MessageInputLog(
                    user_id=user.id,
                    raw_text=text,
                )
            )
            await session.commit()
    except Exception as e:
        logger.error(f"Не удалось сохранить лог сообщения пользователя {user_max_id}: {e}")
