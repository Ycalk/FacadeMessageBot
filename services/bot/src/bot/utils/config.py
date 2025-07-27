import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()


class Config:
    """Service configuration class."""

    BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")
    MAX_MESSAGE_LENGTH: Final[int] = int(os.getenv("MAX_MESSAGE_LENGTH", 120))

    if BOT_TOKEN == "":
        raise ValueError("BOT_TOKEN environment variable is not set")
