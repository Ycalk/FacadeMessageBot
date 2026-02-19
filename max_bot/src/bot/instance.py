import asyncio
from maxapi import Bot, Dispatcher
from redis.asyncio import Redis

from core.config import Config
from services.name_validator import NameValidator
from services.cities_client import CitiesClient
from services.redis_context import RedisContext
from services.antispam import AntiSpam

bot = Bot(Config.BOT_TOKEN)
dispatcher = Dispatcher()

# Семафор для обычных сообщений (ответы пользователям)
_message_semaphore = asyncio.Semaphore(Config.BOT_MESSAGE_CONCURRENCY)
# Семафор для отправки фото (тяжёлые вложения, строже)
_photo_semaphore = asyncio.Semaphore(Config.BOT_PHOTO_CONCURRENCY)


async def send_message(user_id: int, **kwargs) -> None:
    """Отправка сообщения через бот с ограничением параллельных запросов."""
    async with _message_semaphore:
        return await bot.send_message(user_id=user_id, **kwargs)


async def send_photo_message(user_id: int, **kwargs) -> None:
    """Отправка сообщения с фото через бот со строгим ограничением (тяжёлые вложения)."""
    async with _photo_semaphore:
        return await bot.send_message(user_id=user_id, **kwargs)

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
