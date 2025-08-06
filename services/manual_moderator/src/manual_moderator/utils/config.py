import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()


class Config:
    # RabbitMQ configuration
    RABBIT_HOST: Final[str] = os.getenv("RABBIT_HOST", "localhost")
    RABBIT_PORT: Final[int] = int(os.getenv("RABBIT_PORT", 5672))
    RABBIT_USER: Final[str] = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASSWORD: Final[str] = os.getenv("RABBIT_PASSWORD", "guest")

    # Secrets
    BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")
    MAIN_ADMIN_ID: Final[int] = int(os.getenv("MAIN_ADMIN_ID", 0))

    # Redis configuration
    REDIS_HOST: Final[str] = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: Final[int] = int(os.getenv("REDIS_PORT", 6379))
    REDIS_FSM_STORAGE_DB: Final[int] = int(os.getenv("REDIS_FSM_STORAGE_DB", 0))
    REDIS_USER_STORAGE_DB: Final[int] = int(os.getenv("REDIS_USER_STORAGE_DB", 1))

    if BOT_TOKEN == "":
        raise ValueError("BOT_TOKEN must be set in the environment variables.")

    if MAIN_ADMIN_ID == 0:
        raise ValueError("ADMIN_ID must be set in the environment variables.")
