"""Сервис для получения статистики."""

from sqlalchemy import func, select

from db.models import Message, User
from db.session import async_session


async def load_stats() -> dict:
    """Загружает сводную статистику из БД."""
    async with async_session() as session:
        total_messages = await session.scalar(select(func.count(Message.id)))
        total_users = await session.scalar(select(func.count(User.id)))

        status_result = await session.execute(
            select(Message.status, func.count(Message.id)).group_by(Message.status)
        )
        by_status = dict(status_result.all())

        waiting_for_photo = await session.scalar(
            select(func.count(Message.id)).where(
                Message.shown_on_facade == True,  # noqa: E712
                Message.photo_sent == False,  # noqa: E712
                Message.want_photo == True,  # noqa: E712
            )
        )

        photo_sent_count = await session.scalar(
            select(func.count(Message.id)).where(
                Message.photo_sent == True,  # noqa: E712
            )
        )

        return {
            'total_messages': total_messages or 0,
            'total_users': total_users or 0,
            'by_status': by_status,
            'waiting_for_photo': waiting_for_photo or 0,
            'photo_sent_count': photo_sent_count or 0,
        }
