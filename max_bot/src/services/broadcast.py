"""Сервис массовой рассылки уведомлений пользователям."""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select, update

from bot.instance import send_message
from bot.texts import Texts
from core.logger import get_logger
from db.models import Message, MessageStatus, User
from db.session import async_session
from services.app_settings import MARCH_REMINDER_SENT_KEY, set_setting

logger = get_logger(__name__)

# Пауза при получении 429 (умножается на номер попытки)
_RATE_LIMIT_BASE_PAUSE = 5.0


async def _send_with_retry(user_id: int, text: str, max_retries: int = 3) -> str:
    """
    Отправляет сообщение с retry при 429.

    Returns:
        'sent'    — успешно отправлено
        'skipped' — чат не найден (пользователь не запускал бота / заблокировал)
        'error'   — другая ошибка, все попытки исчерпаны
    """
    for attempt in range(max_retries):
        try:
            await send_message(user_id=user_id, text=text)
            return 'sent'
        except Exception as e:
            err = str(e).lower()
            if '404' in err or 'chat.not.found' in err or 'not.found' in err:
                logger.warning(
                    f"Пользователь {user_id} недоступен (чат не найден), пропускаем"
                )
                return 'skipped'
            if '429' in err or 'too.many.requests' in err or 'too_many' in err:
                wait = _RATE_LIMIT_BASE_PAUSE * (attempt + 1)
                logger.warning(
                    f"Rate limit при отправке пользователю {user_id}, "
                    f"ждём {wait:.0f}с (попытка {attempt + 1}/{max_retries})"
                )
                await asyncio.sleep(wait)
                continue
            logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
            return 'error'

    logger.error(f"Все попытки отправки пользователю {user_id} исчерпаны")
    return 'error'


async def send_march_reminder(stream_url: str) -> int:
    """
    Рассылает напоминание о показе всем пользователям с одобренными сообщениями.
    Дедуплицирует по пользователю — один пользователь получает одно сообщение.
    Пропускает пользователей, которым уже отправлено (reminder_sent=True).
    Скорость — не более 5 сообщений в секунду.

    Returns:
        Количество успешно отправленных сообщений (без учёта skipped)
    """
    async with async_session() as session:
        result = await session.execute(
            select(Message, User)
            .join(User, Message.user_id == User.id)
            .where(
                Message.status == MessageStatus.APPROVED,
                Message.reminder_sent.is_(False),
            )
        )
        rows = result.all()

    # Дедупликация: один пользователь — одно сообщение
    seen_users: dict[int, User] = {}
    for _, user in rows:
        if user.id not in seen_users:
            seen_users[user.id] = user

    if not seen_users:
        logger.info("Рассылка напоминания: нет пользователей с одобренными сообщениями")
        return 0

    text = Texts.Messages.march_reminder.format(stream_url=stream_url)

    # user_id (internal DB id) для обновления reminder_sent
    done_user_ids: list[int] = []  # sent + skipped (оба не требуют повтора)
    sent = 0
    skipped = 0
    errors = 0

    for user in seen_users.values():
        outcome = await _send_with_retry(user.max_id, text)
        if outcome == 'sent':
            done_user_ids.append(user.id)
            sent += 1
        elif outcome == 'skipped':
            done_user_ids.append(user.id)
            skipped += 1
        else:
            errors += 1


    # Помечаем reminder_sent=True у всех, кому отправили или кто недоступен
    if done_user_ids:
        async with async_session() as session:
            await session.execute(
                update(Message)
                .where(
                    Message.user_id.in_(done_user_ids),
                    Message.status == MessageStatus.APPROVED,
                )
                .values(reminder_sent=True)
            )
            await session.commit()

    # Сохраняем время последней рассылки
    sent_at = datetime.now(timezone.utc).isoformat()
    await set_setting(MARCH_REMINDER_SENT_KEY, sent_at)

    logger.info(
        f"Рассылка напоминания завершена: {sent} отправлено, "
        f"{skipped} недоступно, {errors} ошибок"
    )
    return sent
