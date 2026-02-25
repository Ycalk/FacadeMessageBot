import asyncio
from maxapi import Bot, Dispatcher
from redis.asyncio import Redis

from core.config import Config
from core.logger import get_logger
from services.name_validator import NameValidator
from services.cities_client import CitiesClient
from services.redis_context import RedisContext
from services.antispam import AntiSpam

logger = get_logger(__name__)

bot = Bot(Config.BOT_TOKEN)
dispatcher = Dispatcher()

_RATE_LIMIT_BASE_PAUSE = 5.0
_SEND_MAX_RETRIES = 3


async def _send_with_retry(user_id: int, **kwargs) -> None:
    """Отправляет сообщение через бот с retry при 429."""
    for attempt in range(_SEND_MAX_RETRIES):
        try:
            return await bot.send_message(user_id=user_id, **kwargs)
        except Exception as e:
            err = str(e).lower()
            if '429' in err or 'too.many.requests' in err or 'too_many' in err:
                wait = _RATE_LIMIT_BASE_PAUSE * (attempt + 1)
                logger.warning(f"Rate limit для {user_id}, ждём {wait:.0f}с (попытка {attempt + 1}/{_SEND_MAX_RETRIES})")
                await asyncio.sleep(wait)
                continue
            raise
    raise RuntimeError(f"Все {_SEND_MAX_RETRIES} попытки отправки пользователю {user_id} исчерпаны")


async def send_message(user_id: int, **kwargs) -> None:
    await _send_with_retry(user_id, **kwargs)


async def send_photo_message(user_id: int, **kwargs) -> None:
    await _send_with_retry(user_id, **kwargs)

redis = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
)

name_validator = NameValidator(Config.NAMES_FILE_PATH)
cities_client = CitiesClient(Config.CITIES_SERVICE_URL)
antispam = AntiSpam(redis)


def get_context(user_id: int) -> RedisContext:
    return RedisContext(redis, chat_id=None, user_id=user_id, ttl=Config.REDIS_CONTEXT_TTL)
