"""Сервис для получения статистики."""

from sqlalchemy import func, select

from db.models import Message, MessageStatus, User
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
            'by_status': by_status,  # Текущее распределение
            'passed_by_status': passed_by_status,  # Сколько сообщений достигло этапа
            'waiting_for_photo': waiting_for_photo or 0,
            'photo_sent_count': photo_sent_count or 0,
        }
