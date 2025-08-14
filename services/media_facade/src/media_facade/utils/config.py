import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()


class Config:
    # RabbitMQ configuration
    RABBIT_PORT: Final[int] = int(os.getenv("RABBIT_PORT", 5672))
    RABBIT_HOST: Final[str] = os.getenv("RABBIT_HOST", "localhost")
    RABBIT_USER: Final[str] = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASSWORD: Final[str] = os.getenv("RABBIT_PASSWORD", "guest")

    # PostgreSQL configuration
    POSTGRES_HOST: Final[str] = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: Final[int] = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER: Final[str] = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: Final[str] = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: Final[str] = os.getenv("POSTGRES_DB", "")

    PORT: Final[int] = int(os.getenv("PORT", 8000))
    MEDIA_FACADE_API_BASE_URL: Final[str] = os.getenv("MEDIA_FACADE_API_BASE_URL", "")
    MEDIA_FACADE_API_TOKEN: Final[str] = os.getenv("MEDIA_FACADE_API_TOKEN", "")
    SECRET_KEY: Final[str] = os.getenv("SECRET_KEY", "")

    USE_MOCK: Final[bool] = os.getenv("USE_MOCK", "0") == "1"
    MEDIA_FACADE_API_MOCK_BASE_URL: Final[str] = f"http://localhost:{PORT}/api/vk"
    SELF_MOCK_URL: Final[str] = f"http://localhost:{PORT}/api/v1/webhook"
    MAX_TEXT_LENGTH: Final[int] = int(os.getenv("MAX_TEXT_LENGTH", 80))
    MAX_NAME_AND_CITY_LENGTH: Final[int] = int(
        os.getenv("MAX_NAME_AND_CITY_LENGTH", 15)
    )

    if MEDIA_FACADE_API_TOKEN == "":
        raise ValueError(
            "MEDIA_FACADE_API_TOKEN must be set in the environment variables."
        )

    if MEDIA_FACADE_API_BASE_URL == "" and not USE_MOCK:
        raise ValueError(
            "MEDIA_FACADE_API_BASE_URL must be set in the environment variables or USE_MOCK must be enabled."
        )

    if SECRET_KEY == "":
        raise ValueError("SECRET_KEY must be set in the environment variables.")
