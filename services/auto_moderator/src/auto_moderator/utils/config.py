import os
from dotenv import load_dotenv
from typing import Final

load_dotenv()


class Config:
    MISTRAL_API_KEY: Final[str] = os.getenv("MISTRAL_API_KEY", "")

    # RabbitMQ configuration
    RABBIT_PORT: Final[int] = int(os.getenv("RABBIT_PORT", 5672))
    RABBIT_HOST: Final[str] = os.getenv("RABBIT_HOST", "localhost")
    RABBIT_USER: Final[str] = os.getenv("RABBIT_USER", "guest")
    RABBIT_PASSWORD: Final[str] = os.getenv("RABBIT_PASSWORD", "guest")

    if MISTRAL_API_KEY == "":
        raise ValueError("MISTRAL_KEY must be set in the environment variables.")
