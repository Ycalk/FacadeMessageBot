from pytest import fixture
from aiomax import Bot
from dotenv import load_dotenv
import os
import logging

load_dotenv()


@fixture(scope="session")
def bot() -> Bot:
    return Bot(os.getenv("TOKEN", ""), logging_level=logging.DEBUG)
