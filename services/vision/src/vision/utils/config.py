import os
from dotenv import load_dotenv
from typing import Final
from zoneinfo import ZoneInfo

load_dotenv()


class Config:
    TIME_ZONE: Final[ZoneInfo] = ZoneInfo(os.getenv("TIME_ZONE", "Europe/Moscow"))
    ANALYTICS_DELAY_SECONDS: Final[int] = int(os.getenv("ANALYTICS_DELAY_SECONDS", 120))
    RTMP_URL: Final[str] = os.getenv("RTMP_URL", "rtmp://localhost:1935/live")

    # RabbitMQ configuration
    RABBIT_PORT: Final[int] = int(os.getenv("RABBIT_PORT", 5672))
    RABBIT_HOST: Final[str] = os.getenv("RABBIT_HOST", "localhost")
    RABBIT_USER: Final[str] = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASSWORD: Final[str] = os.getenv("RABBIT_PASSWORD", "guest")

    # Redis configuration
    REDIS_HOST: Final[str] = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: Final[int] = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DATA_STORAGE_DB: Final[int] = int(os.getenv("REDIS_BLACK_LIST_STORAGE_DB", 0))
