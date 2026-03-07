"""Сервис массовой рассылки уведомлений пользователям."""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select, update

from maxapi.enums.parse_mode import ParseMode

from bot.instance import send_message
from bot.texts import Texts
from core.logger import get_logger
from db.models import Message, MessageStatus, User
from db.session import async_session
from services.app_settings import MARCH_REMINDER_SENT_KEY, OVERLOAD_BROADCAST_SENT_KEY, set_setting

logger = get_logger(__name__)

# Максимум параллельных отправок при рассылке
_BROADCAST_CONCURRENCY = 30
_broadcast_semaphore = asyncio.Semaphore(_BROADCAST_CONCURRENCY)


async def _send_one_safe(user_id: int, text: str, parse_mode: ParseMode | None = None) -> str:
    """
    Отправляет сообщение одному пользователю. Retry при 429 встроен в send_message.

    Returns:
        'sent'    — успешно отправлено
        'skipped' — чат не найден (пользователь не запускал бота / заблокировал)
        'error'   — другая ошибка
    """
    try:
        kwargs = {"text": text}
        if parse_mode is not None:
            kwargs["parse_mode"] = parse_mode
        await send_message(user_id=user_id, **kwargs)
        return 'sent'
    except Exception as e:
        err = str(e).lower()
        if '404' in err or 'chat.not.found' in err or 'not.found' in err:
            logger.warning(f"Пользователь {user_id} недоступен (чат не найден), пропускаем")
            return 'skipped'
        logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
        return 'error'


async def send_march_reminder(stream_url: str) -> int:
    """
    Рассылает напоминание о показе всем пользователям с одобренными сообщениями.
    Дедуплицирует по пользователю — один пользователь получает одно сообщение.
    Пропускает пользователей, которым уже отправлено (reminder_sent=True).
    Параллельность — до 30 одновременных отправок.

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

    results: dict[int, str] = {}  # user.id → outcome

    async def _send_one(user: User) -> None:
        async with _broadcast_semaphore:
            results[user.id] = await _send_one_safe(user.max_id, text)

    await asyncio.gather(*[_send_one(u) for u in seen_users.values()])

    done_user_ids = [uid for uid, outcome in results.items() if outcome in ('sent', 'skipped')]
    sent = sum(1 for o in results.values() if o == 'sent')
    skipped = sum(1 for o in results.values() if o == 'skipped')
    errors = sum(1 for o in results.values() if o == 'error')

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


_OVERLOAD_TEXT = (
    "Ваша активность превзошла все ожидания — свободные места на медиафасаде разлетелись "
    "в считанные мгновения, и экран полностью забронирован до конца праздника. "
    "Если вы не успели попасть в эфир, воспользуйтесь "
    "[Конструктором открыток от МАХ](https://max.ru/maxpostcards_bot): "
    "создайте своё поздравление и отправьте его лично! "
    "Следите за новостями в [нашем канале](https://max.ru/max_news) — "
    "впереди ещё много активностей. С праздником! 🌷"
)


async def send_overload_broadcast() -> int:
    """
    Рассылает уведомление о перегрузке фасада пользователям, чьи сообщения
    находятся в статусе internal_moderation или vk_moderation.
    После отправки меняет статус сообщения на overload.
    Повторная рассылка безопасна — такие сообщения уже в статусе overload и не попадут в выборку.

    Returns:
        Количество успешно отправленных сообщений.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Message, User)
            .join(User, Message.user_id == User.id)
            .where(
                Message.status.in_([MessageStatus.INTERNAL_MODERATION, MessageStatus.VK_MODERATION]),
            )
        )
        rows = result.all()

    # Дедупликация: один пользователь — одно сообщение (берём все его message_ids)
    seen_users: dict[int, User] = {}
    user_message_ids: dict[int, list[int]] = {}
    for msg, user in rows:
        if user.id not in seen_users:
            seen_users[user.id] = user
            user_message_ids[user.id] = []
        user_message_ids[user.id].append(msg.id)

    if not seen_users:
        logger.info("Рассылка перегрузки: нет пользователей в ожидающих статусах")
        return 0

    results: dict[int, str] = {}  # user.id → outcome

    async def _send_one(user: User) -> None:
        async with _broadcast_semaphore:
            results[user.id] = await _send_one_safe(user.max_id, _OVERLOAD_TEXT, ParseMode.MARKDOWN)

    await asyncio.gather(*[_send_one(u) for u in seen_users.values()])

    sent = sum(1 for o in results.values() if o == 'sent')
    skipped = sum(1 for o in results.values() if o == 'skipped')
    errors = sum(1 for o in results.values() if o == 'error')

    # Меняем статус на overload у всех, кому отправили или кто недоступен
    done_message_ids = [
        mid
        for uid, outcome in results.items()
        if outcome in ('sent', 'skipped')
        for mid in user_message_ids.get(uid, [])
    ]
    if done_message_ids:
        async with async_session() as session:
            await session.execute(
                update(Message)
                .where(Message.id.in_(done_message_ids))
                .values(status=MessageStatus.OVERLOAD)
            )
            await session.commit()

    sent_at = datetime.now(timezone.utc).isoformat()
    await set_setting(OVERLOAD_BROADCAST_SENT_KEY, sent_at)

    logger.info(
        f"Рассылка перегрузки завершена: {sent} отправлено, "
        f"{skipped} недоступно, {errors} ошибок"
    )
    return sent
