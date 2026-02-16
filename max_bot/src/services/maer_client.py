"""Клиент для работы с Maer API (внешняя модерация)."""

import httpx
from typing import Optional

from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


class MaerAPIError(Exception):
    """Ошибка при работе с Maer API."""
    pass


async def send_to_maer_moderation(
    message_id: int,
    name: str,
    city: str,
    text: str,
    layout: int,
) -> bool:
    """
    Отправка сообщения на внешнюю модерацию через Maer API.

    Args:
        message_id: ID сообщения в нашей БД
        name: Имя автора
        city: Город автора
        text: Текст сообщения
        layout: ID подложки креатива (frame_id)

    Returns:
        True если успешно отправлено, False в случае ошибки

    Raises:
        MaerAPIError: При ошибках API
    """
    if not Config.MAER_API_URL or not Config.MAER_API_TOKEN:
        logger.warning("Maer API не настроен, пропускаем отправку на модерацию")
        return False

    url = f"{Config.MAER_API_URL}/api/vk/message"
    headers = {
        "x-token": Config.MAER_API_TOKEN,
        "Content-Type": "application/json",
    }

    payload = {
        "id": message_id,
        "name": name,
        "city": city,
        "text": text,
        "layout": layout,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                logger.info(f"Сообщение {message_id} успешно отправлено на модерацию Maer")
                return True
            elif response.status_code == 401:
                logger.error(f"Ошибка авторизации Maer API: неверный токен")
                raise MaerAPIError("Токен не корректный")
            elif response.status_code == 430:
                logger.error(f"Текст сообщения {message_id} превышает лимит в 120 символов")
                raise MaerAPIError("Текст сообщения превышает лимит в 120 символов")
            elif response.status_code == 431:
                logger.error(f"Имя или город {message_id} превышает лимит в 20 символов")
                raise MaerAPIError("Имя или город превышает лимит в 20 символов")
            elif response.status_code == 422:
                logger.error(f"Неправильные поля или формат json для сообщения {message_id}")
                raise MaerAPIError("Неправильные поля или формат json")
            elif response.status_code == 400:
                logger.error(f"Не корректные параметры запроса для сообщения {message_id}")
                raise MaerAPIError("Не корректные параметры запроса")
            else:
                logger.error(
                    f"Неожиданный ответ от Maer API: {response.status_code}, "
                    f"тело: {response.text}"
                )
                raise MaerAPIError(f"Неожиданный код ответа: {response.status_code}")

    except httpx.TimeoutException:
        logger.error(f"Таймаут при отправке сообщения {message_id} на модерацию Maer")
        raise MaerAPIError("Таймаут соединения с Maer API")
    except httpx.RequestError as e:
        logger.error(f"Ошибка сети при отправке на модерацию Maer: {e}")
        raise MaerAPIError(f"Ошибка сети: {e}")
