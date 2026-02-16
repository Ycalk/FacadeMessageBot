from maxapi import Bot, Dispatcher
from redis.asyncio import Redis

from core.config import Config
from services.name_validator import NameValidator
from services.cities_client import CitiesClient
from services.redis_context import RedisContext

bot = Bot(Config.BOT_TOKEN)
dispatcher = Dispatcher()

redis = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
)

name_validator = NameValidator(Config.NAMES_FILE_PATH)
cities_client = CitiesClient(Config.CITIES_SERVICE_URL)


def get_context(user_id: int) -> RedisContext:
    return RedisContext(redis, chat_id=None, user_id=user_id, ttl=Config.REDIS_CONTEXT_TTL)
