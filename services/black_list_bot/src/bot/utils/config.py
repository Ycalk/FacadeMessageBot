import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()


class Config:
    """Service configuration class."""

    # RabbitMQ configuration
    RABBIT_HOST: Final[str] = os.getenv("RABBIT_HOST", "localhost")
    RABBIT_PORT: Final[int] = int(os.getenv("RABBIT_PORT", 5672))
    RABBIT_USER: Final[str] = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASSWORD: Final[str] = os.getenv("RABBIT_PASSWORD", "guest")

    # Secrets
    BLACK_LIST_BOT_TOKEN: Final[str] = os.getenv("BLACK_LIST_BOT_TOKEN", "")
    BLACK_LIST_BOT_SECRET_KEY: Final[str] = os.getenv("BLACK_LIST_BOT_SECRET_KEY", "")

    # Redis configuration
    REDIS_HOST: Final[str] = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: Final[int] = int(os.getenv("REDIS_PORT", 6379))
    REDIS_USER_STORAGE_DB: Final[int] = int(os.getenv("REDIS_USER_STORAGE_DB", 0))

    if BLACK_LIST_BOT_TOKEN == "":
        raise ValueError("BOT_TOKEN must be set in the environment variables.")

    if BLACK_LIST_BOT_SECRET_KEY == "":
        raise ValueError("SECRET_KEY must be set in the environment variables.")
