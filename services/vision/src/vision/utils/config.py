import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()


class Config:
    ANALYTICS_DELAY_SECONDS: Final[int] = int(os.getenv("ANALYTICS_DELAY_SECONDS", 120))
    MAXIMUM_IMAGE_STORAGE_TIME_SECONDS: Final[int] = ANALYTICS_DELAY_SECONDS + 60
    RTMP_URL: Final[str] = os.getenv("RTMP_URL", "rtmp://localhost/live")
    VIDEO_WIDTH: Final[int] = int(os.getenv("VIDEO_WIDTH", 800))
    VIDEO_HEIGHT: Final[int] = int(os.getenv("VIDEO_HEIGHT", 1340))
    VIDEO_FPS: Final[int] = int(os.getenv("VIDEO_FPS", 23))
    VIDEO_CHANNELS: Final[int] = int(os.getenv("VIDEO_CHANNELS", 3))
    DEBUG_MODE: Final[bool] = os.getenv("DEBUG_MODE", "0").lower() == "1"

    FONT_PATH: Final[str] = os.getenv(
        "FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    # RabbitMQ configuration
    RABBIT_PORT: Final[int] = int(os.getenv("RABBIT_PORT", 5672))
    RABBIT_HOST: Final[str] = os.getenv("RABBIT_HOST", "localhost")
    RABBIT_USER: Final[str] = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASSWORD: Final[str] = os.getenv("RABBIT_PASSWORD", "guest")

    # Redis configuration
    REDIS_HOST: Final[str] = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: Final[int] = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DATA_STORAGE_DB: Final[int] = int(os.getenv("REDIS_BLACK_LIST_STORAGE_DB", 0))
