from aiomax import Bot
from .utils import Config
import logging
from faststream.rabbit import RabbitBroker
from faststream.security import SASLPlaintext
from redis.asyncio import Redis


bot = Bot(Config.BOT_TOKEN, logging_level=logging.DEBUG)
broker = RabbitBroker(
    host=Config.RABBIT_HOST,
    port=Config.RABBIT_PORT,
    security=SASLPlaintext(
        username=Config.RABBIT_USER,
        password=Config.RABBIT_PASSWORD,
    ),
)
redis = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_USER_STORAGE_DB,
)
