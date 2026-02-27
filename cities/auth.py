"""Bearer авторизация для Cities API."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings

_bearer_scheme = HTTPBearer()


async def _check_token(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    """Проверяет Bearer токен из заголовка Authorization."""
    if not settings.cities_api_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис не настроен: CITIES_API_TOKEN не задан",
        )

    if credentials.credentials != settings.cities_api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен авторизации",
        )

    return credentials.credentials


verify_api_token = Depends(_check_token)
