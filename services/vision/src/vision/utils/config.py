import os
from dotenv import load_dotenv
from typing import Final
from zoneinfo import ZoneInfo

load_dotenv()


class Config:
    TIME_ZONE: Final[ZoneInfo] = ZoneInfo(os.getenv("TIME_ZONE", "Europe/Moscow"))
    ANALYTICS_DELAY_SECONDS: Final[int] = int(os.getenv("ANALYTICS_DELAY_SECONDS", 120))
    MAXIMUM_IMAGE_STORAGE_TIME_SECONDS: Final[int] = ANALYTICS_DELAY_SECONDS + 60
    RTMP_URL: Final[str] = os.getenv("RTMP_URL", "rtmp://localhost/live")
    VIDEO_WIDTH: Final[int] = int(os.getenv("VIDEO_WIDTH", 640))
    VIDEO_HEIGHT: Final[int] = int(os.getenv("VIDEO_HEIGHT", 360))
    VIDEO_FPS: Final[int] = int(os.getenv("VIDEO_FPS", 10))
    VIDEO_CHANNELS: Final[int] = int(os.getenv("VIDEO_CHANNELS", 3))
    DEBUG_MODE: Final[bool] = os.getenv("DEBUG_MODE", "0").lower() == "1"

    # RabbitMQ configuration
    RABBIT_PORT: Final[int] = int(os.getenv("RABBIT_PORT", 5672))
    RABBIT_HOST: Final[str] = os.getenv("RABBIT_HOST", "localhost")
    RABBIT_USER: Final[str] = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASSWORD: Final[str] = os.getenv("RABBIT_PASSWORD", "guest")

    # Redis configuration
    REDIS_HOST: Final[str] = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: Final[int] = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DATA_STORAGE_DB: Final[int] = int(os.getenv("REDIS_BLACK_LIST_STORAGE_DB", 0))
