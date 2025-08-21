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

    # Redis configuration
    REDIS_HOST: Final[str] = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: Final[int] = int(os.getenv("REDIS_PORT", 6379))
    REDIS_STORAGE_DB: Final[int] = int(os.getenv("REDIS_BLACK_LIST_STORAGE_DB", 0))

    # Secrets
    GOOGLE_ACCOUNT_CREDENTIALS: Final[str] = os.getenv("GOOGLE_ACCOUNT_CREDENTIALS", "")
    GOOGLE_SHEET_ID: Final[str] = os.getenv("GOOGLE_SHEET_ID", "")

    if GOOGLE_ACCOUNT_CREDENTIALS == "":
        raise ValueError(
            "GOOGLE_ACCOUNT_CREDENTIALS must be set in the environment variables."
        )

    if GOOGLE_SHEET_ID == "":
        raise ValueError("GOOGLE_SHEET_ID must be set in the environment variables.")
