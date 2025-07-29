import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()


class Config:
    """Service configuration class."""

    BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")

    MAX_MESSAGE_LENGTH: Final[int] = int(os.getenv("MAX_MESSAGE_LENGTH", 80))
    MAX_NAME_LENGTH: Final[int] = int(os.getenv("MAX_NAME_LENGTH", 15))
    MAX_CITY_LENGTH: Final[int] = int(os.getenv("MAX_CITY_LENGTH", 15))

    COORDINATE_EXTRACTOR_URL: Final[str] = os.getenv(
        "COORDINATE_EXTRACTOR_URL", "https://nominatim.openstreetmap.org/reverse"
    )

    NAME_API_URL: Final[str] = os.getenv(
        "NAME_API_URL", "https://api.nameapi.org/rest/v5.3/parser/personnameparser"
    )
    NAME_API_KEY: Final[str] = os.getenv("NAME_API_KEY", "")
    MINIMAL_NAME_CONFIDENCE: Final[float] = float(
        os.getenv("MINIMAL_NAME_CONFIDENCE", 0.6)
    )

    if BOT_TOKEN == "":
        raise ValueError("BOT_TOKEN environment variable is not set")

    if NAME_API_KEY == "":
        raise ValueError("NAME_API_KEY environment variable is not set")
