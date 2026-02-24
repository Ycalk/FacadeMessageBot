"""Сервис автоматической модерации сообщений."""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select

from core.config import Config
from core.logger import get_logger
from db.models import Message, MessageStatus
from db.session import async_session
from services.mistral_moderator import moderate_with_mistral

logger = get_logger(__name__)


async def auto_moderate_message(message_id: int, max_retries: int = 3) -> bool:
    """
    Автоматическая модерация сообщения с retry механизмом.

    После прохождения автомодерации статус меняется на:
    - INTERNAL_MODERATION если одобрено
    - REJECTED если отклонено

    Args:
        message_id: ID сообщения для модерации
        max_retries: Максимальное количество повторных попыток при ошибках

    Returns:
        True если сообщение одобрено, False если отклонено
    """
    retry_count = 0
    last_error = None

    while retry_count < max_retries:
        try:
            async with async_session() as session:
                result = await session.execute(
                    select(Message).where(Message.id == message_id)
                )
                message = result.scalar_one_or_none()

                if not message:
                    logger.error(f"Сообщение {message_id} не найдено для автомодерации")
                    return False

                if message.status != MessageStatus.AUTO_MODERATION:
                    logger.warning(
                        f"Сообщение {message_id} не в статусе автомодерации (текущий: {message.status})"
                    )
                    return False

                # Модерация через Mistral AI
                moderation_result = await moderate_with_mistral(
                    text=message.text,
                    name=message.name,
                    city=message.city
                )

                approved = moderation_result.get("approved", False)
                reason = moderation_result.get("reason", "")

                if not approved:
                    # Mistral отклонил - сразу отклоняем
                    logger.warning(
                        f"Сообщение {message_id} отклонено Mistral: {reason}"
                    )
                    message.status = MessageStatus.REJECTED
                    await session.commit()
                    logger.info(f"Сообщение {message_id} отклонено автомодерацией")

                    from api.utils import send_rejection_notification
                    await send_rejection_notification(message_id)

                    return False

                # Mistral одобрил — отправляем на внутреннюю модерацию
                message.status = MessageStatus.INTERNAL_MODERATION
                logger.info(
                    f"Сообщение {message_id} прошло Mistral → внутренняя модерация"
                )

                await session.commit()

                # Применяем автоодобрение от настроенных модераторов
                await _apply_auto_approvals(message_id)

                return approved

        except Exception as e:
            retry_count += 1
            last_error = e
            logger.error(
                f"Ошибка при автомодерации сообщения {message_id} "
                f"(попытка {retry_count}/{max_retries}): {e}"
            )

            if retry_count < max_retries:
                # Экспоненциальная задержка между попытками
                await asyncio.sleep(2 ** retry_count)
            else:
                # Исчерпаны все попытки - устанавливаем fallback статус
                logger.error(
                    f"Все попытки автомодерации сообщения {message_id} исчерпаны. "
                    f"Переводим в fallback статус. Последняя ошибка: {last_error}"
                )
                await _set_fallback_status(message_id)
                return False

    return False


async def _apply_auto_approvals(message_id: int) -> None:
    """Применяет автоодобрения от модераторов с включённым автоапрувом."""
    from services.app_settings import get_auto_approve_moderators
    from services.internal_moderator import moderate_by_moderator

    auto_mods = await get_auto_approve_moderators()
    if not auto_mods:
        return

    for mod_id in auto_mods:
        if mod_id in Config.moderators_list:
            result = await moderate_by_moderator(message_id, mod_id, True)
            if result.get("success"):
                logger.info(f"Автоодобрение сообщения {message_id} модератором {mod_id!r}")


async def _set_fallback_status(message_id: int) -> None:
    """
    Устанавливает fallback статус при ошибках автомодерации.
    Отправляет сообщение на внутреннюю модерацию.
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Message).where(Message.id == message_id)
            )
            message = result.scalar_one_or_none()

            if message:
                message.status = MessageStatus.INTERNAL_MODERATION
                logger.warning(
                    f"Сообщение {message_id} отправлено на внутреннюю модерацию "
                    f"(fallback после ошибки автомодерации)"
                )
                await session.commit()
                await _apply_auto_approvals(message_id)
    except Exception as e:
        logger.critical(
            f"Критическая ошибка при установке fallback статуса для сообщения {message_id}: {e}"
        )


async def recover_stuck_messages() -> int:
    """
    Восстановление зависших сообщений при старте бота.

    Находит все сообщения в статусе AUTO_MODERATION старше заданного таймаута
    и запускает их повторную обработку.

    Returns:
        Количество восстановленных сообщений
    """
    timeout_minutes = Config.AUTO_MODERATION_STUCK_TIMEOUT_MINUTES
    timeout = datetime.now() - timedelta(minutes=timeout_minutes)

    try:
        async with async_session() as session:
            result = await session.execute(
                select(Message)
                .where(Message.status == MessageStatus.AUTO_MODERATION)
                .where(Message.created_at < timeout)
            )
            stuck_messages = result.scalars().all()

            if not stuck_messages:
                logger.info("Зависших сообщений не найдено")
                return 0

            count = len(stuck_messages)
            logger.warning(
                f"Найдено {count} зависших сообщений в статусе AUTO_MODERATION "
                f"старше {timeout_minutes} минут. Запуск повторной обработки..."
            )

            # Запускаем обработку всех зависших сообщений в фоне
            for message in stuck_messages:
                asyncio.create_task(auto_moderate_message(message.id))
                logger.info(f"Запущена повторная обработка сообщения {message.id}")

            logger.info(f"Восстановление завершено: {count} сообщений отправлено на обработку")
            return count

    except Exception as e:
        logger.error(f"Ошибка при восстановлении зависших сообщений: {e}")
        return 0
