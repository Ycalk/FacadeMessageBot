import os
from dotenv import load_dotenv
from typing import Final
from zoneinfo import ZoneInfo

load_dotenv()


class Config:
    """Service configuration class."""

    TIME_ZONE: Final[ZoneInfo] = ZoneInfo(os.getenv("TIME_ZONE", "Europe/Moscow"))
    # RabbitMQ configuration
    RABBIT_HOST: Final[str] = os.getenv("RABBIT_HOST", "localhost")
    RABBIT_PORT: Final[int] = int(os.getenv("RABBIT_PORT", 5672))
    RABBIT_USER: Final[str] = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASSWORD: Final[str] = os.getenv("RABBIT_PASSWORD", "guest")

    # PostgreSQL configuration
    POSTGRES_HOST: Final[str] = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: Final[int] = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER: Final[str] = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: Final[str] = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: Final[str] = os.getenv("POSTGRES_DB", "")

    # Secrets
    BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")
    NAME_API_KEY: Final[str] = os.getenv("NAME_API_KEY", "")

    # Other configurations
    MAX_MESSAGE_LENGTH: Final[int] = int(os.getenv("MAX_MESSAGE_LENGTH", 80))
    MAX_NAME_LENGTH: Final[int] = int(os.getenv("MAX_NAME_LENGTH", 15))
    MAX_CITY_LENGTH: Final[int] = int(os.getenv("MAX_CITY_LENGTH", 15))
    MINIMAL_NAME_CONFIDENCE: Final[float] = float(
        os.getenv("MINIMAL_NAME_CONFIDENCE", 0.6)
    )
    TERMS_OF_USE_URL: Final[str] = os.getenv(
        "TERMS_OF_USE_URL", "https://example.com/terms-of-use"
    )
    MESSAGES_TIME_OUT_MINUTES: Final[int] = int(
        os.getenv("MESSAGES_TIME_OUT_MINUTES", 1)
    )
    MAXIMUM_MESSAGES_PER_USER: Final[int] = int(
        os.getenv("MAXIMUM_MESSAGES_PER_USER", 3)
    )
    MAXIMUM_ATTEMPTS_PER_MESSAGE: Final[int] = int(
        os.getenv("MAXIMUM_ATTEMPTS_PER_MESSAGE", 3)
    )
    START_MESSAGE_IMAGE_TOKEN: Final[str | None] = os.getenv(
        "START_MESSAGE_IMAGE_TOKEN"
    )

    COORDINATE_EXTRACTOR_URL: Final[str] = os.getenv(
        "COORDINATE_EXTRACTOR_URL", "https://nominatim.openstreetmap.org/reverse"
    )

    NAME_API_URL: Final[str] = os.getenv(
        "NAME_API_URL", "https://api.nameapi.org/rest/v5.3/parser/personnameparser"
    )

    if BOT_TOKEN == "":
        raise ValueError("BOT_TOKEN environment variable is not set")

    if NAME_API_KEY == "":
        raise ValueError("NAME_API_KEY environment variable is not set")

    if POSTGRES_USER == "":
        raise ValueError("POSTGRES_USER environment variable is not set")

    if POSTGRES_PASSWORD == "":
        raise ValueError("POSTGRES_PASSWORD environment variable is not set")

    if POSTGRES_DB == "":
        raise ValueError("POSTGRES_DB environment variable is not set")
