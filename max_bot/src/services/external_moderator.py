"""Сервис внешней модерации."""

import httpx
from sqlalchemy import select

from core.config import Config
from core.logger import get_logger
from db.models import Message, MessageStatus
from db.session import async_session

logger = get_logger(__name__)


async def external_moderate_message(message_id: int) -> bool:
    """
    Внешняя модерация сообщения.

    После прохождения внешней модерации статус меняется на:
    - APPROVED если одобрено
    - REJECTED если отклонено

    Args:
        message_id: ID сообщения для модерации

    Returns:
        True если сообщение одобрено, False если отклонено
    """
    async with async_session() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()

        if not message:
            logger.error(f"Сообщение {message_id} не найдено для внешней модерации")
            return False

        if message.status != MessageStatus.MAER_MODERATION:
            logger.warning(
                f"Сообщение {message_id} не в статусе внешней модерации (текущий: {message.status})"
            )
            return False

        # Отправляем запрос во внешнюю систему модерации
        try:
            external_url = Config.EXTERNAL_MODERATOR_URL
            if external_url:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        external_url,
                        json={
                            "message_id": message_id,
                            "image_url": message.image_url,
                            "text": message.text,
                            "frame_id": message.frame_id,
                            "display_name": message.name,
                            "display_city": message.city,
                        },
                        timeout=10.0
                    )
                logger.info(f"Отправлен запрос на внешнюю модерацию для сообщения {message_id}")
            else:
                logger.warning("EXTERNAL_MODERATOR_URL не настроен, внешняя модерация пропущена")
        except httpx.HTTPError as e:
            logger.error(f"Ошибка при отправке на внешнюю модерацию: {e}")
            # Не прерываем выполнение, просто логируем ошибку

        await session.commit()

    return True
