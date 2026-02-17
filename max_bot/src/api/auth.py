"""Авторизация для API эндпоинтов."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)

_bearer_scheme = HTTPBearer()


async def _check_token(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """Проверяет Bearer токен из заголовка Authorization."""
    if not Config.API_TOKEN:
        logger.warning("API_TOKEN не настроен, авторизация отключена")
        return credentials.credentials

    if credentials.credentials != Config.API_TOKEN:
        logger.warning("Неверный API токен")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен авторизации",
        )

    return credentials.credentials


verify_api_token = Depends(_check_token)
