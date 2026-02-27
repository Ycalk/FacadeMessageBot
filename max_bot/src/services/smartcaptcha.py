"""Проверка токена Yandex SmartCaptcha."""

import httpx

from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)

SMARTCAPTCHA_VALIDATE_URL = "https://smartcaptcha.cloud.yandex.ru/validate"
_TIMEOUT_SECONDS = 5.0


async def validate_smartcaptcha_token(token: str) -> tuple[bool, str]:
    """Валидирует токен SmartCaptcha через серверный API."""
    captcha_token = (token or "").strip()
    if not captcha_token:
        return False, "Подтвердите, что вы не робот"

    if not Config.SMARTCAPTCHA_SERVER_KEY:
        logger.warning("SMARTCAPTCHA_SERVER_KEY не задан")
        return False, "Капча не настроена на сервере"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.post(
                SMARTCAPTCHA_VALIDATE_URL,
                data={"secret": Config.SMARTCAPTCHA_SERVER_KEY, "token": captcha_token},
            )
        response.raise_for_status()
        payload = response.json()
    except Exception as e:
        logger.error(f"Ошибка проверки SmartCaptcha: {e}")
        return False, "Не удалось проверить капчу, попробуйте ещё раз"

    if payload.get("status") == "ok":
        return True, ""

    logger.warning(f"SmartCaptcha отклонена: {payload}")
    return False, "Проверка капчи не пройдена"
