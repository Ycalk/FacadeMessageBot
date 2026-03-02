"""Сервис для получения статистики."""

from datetime import date, datetime, timedelta

from sqlalchemy import func, select, text

from db.models import Message, MessageInputLog, MessageStatus, User
from db.session import async_session


def _has_vk_moderation_record(meta: dict | None) -> bool:
    """Проверяет, что у сообщения есть следы прохождения VK-модерации."""
    if not meta:
        return False
    return bool(meta.get("vk_entered") or meta.get("vk_approvals") or meta.get("vk_rejections"))


async def load_stats() -> dict:
    """Загружает сводную статистику из БД."""
    async with async_session() as session:
        total_messages = await session.scalar(select(func.count(Message.id)))
        total_users = await session.scalar(select(func.count(User.id)))
        message_input_attempts = await session.scalar(select(func.count(MessageInputLog.id)))

        current_status_result = await session.execute(
            select(Message.status, func.count(Message.id)).group_by(Message.status)
        )
        by_status = dict(current_status_result.all())

        rows = await session.execute(select(Message.status, Message.meta))
        messages = rows.all()
        passed_by_status = {status: 0 for status in MessageStatus}
        passed_by_status[MessageStatus.INTERNAL_MODERATION] = len(messages)

        for status, meta in messages:
            has_vk_record = _has_vk_moderation_record(meta)
            has_maer_record = bool(meta and meta.get("maer_rejection_reason"))

            if status in {
                MessageStatus.VK_MODERATION,
                MessageStatus.MAER_MODERATION,
                MessageStatus.APPROVED,
            } or has_vk_record or has_maer_record:
                passed_by_status[MessageStatus.VK_MODERATION] += 1

            if status in {MessageStatus.MAER_MODERATION, MessageStatus.APPROVED} or has_maer_record:
                passed_by_status[MessageStatus.MAER_MODERATION] += 1

            if status == MessageStatus.APPROVED:
                passed_by_status[MessageStatus.APPROVED] += 1

            if status == MessageStatus.REJECTED:
                passed_by_status[MessageStatus.REJECTED] += 1

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
            'message_input_attempts': message_input_attempts or 0,
            'by_status': by_status,  # Текущее распределение
            'passed_by_status': passed_by_status,  # Сколько сообщений достигло этапа
            'waiting_for_photo': waiting_for_photo or 0,
            'photo_sent_count': photo_sent_count or 0,
        }


_MSK = timedelta(hours=3)


async def load_hourly_stats(target_date: date) -> list[dict]:
    """Возвращает количество сообщений по часам за указанный день (UTC+3, все 24 часа)."""
    # Границы дня в UTC: день по МСК — это [day-3h, day+21h) по UTC
    start_utc = datetime(target_date.year, target_date.month, target_date.day) - _MSK
    end_utc = start_utc + timedelta(days=1)

    async with async_session() as session:
        result = await session.execute(
            select(
                func.date_trunc('hour', Message.created_at + text("interval '3 hours'")).label('hour'),
                func.count(Message.id).label('count'),
            )
            .where(Message.created_at >= start_utc, Message.created_at < end_utc)
            .group_by(text('1'))
            .order_by(text('1'))
        )
        rows = result.all()

    hourly: dict[int, int] = {h: 0 for h in range(24)}
    for row in rows:
        hourly[row.hour.hour] = row.count

    return [{'час': f'{h:02d}:00', 'сообщений': hourly[h]} for h in range(24)]
