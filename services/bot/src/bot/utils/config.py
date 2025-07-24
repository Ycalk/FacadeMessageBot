import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()


class Config:
    """Service configuration class."""

    BOT_TOKEN: Final[str] = os.getenv("BOT_TOKEN", "")

    if BOT_TOKEN == "":
        raise ValueError("BOT_TOKEN environment variable is not set")
