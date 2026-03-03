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

_MAX_RETRIES = 3
_RATE_LIMIT_BASE_PAUSE = 5.0


async def _send_with_retry(user_id: int, **kwargs) -> None:
    """Отправляет сообщение через бот. При 429 — retry с экспоненциальной паузой."""
    for attempt in range(_MAX_RETRIES):
        try:
            await bot.send_message(user_id=user_id, **kwargs)
            return
        except Exception as e:
            err = str(e).lower()
            if '429' in err or 'too.many.requests' in err or 'too_many' in err:
                wait = _RATE_LIMIT_BASE_PAUSE * (attempt + 1)
                logger.warning(
                    f"Rate limit MAX API для пользователя {user_id}, "
                    f"ждём {wait:.0f}с (попытка {attempt + 1}/{_MAX_RETRIES})"
                )
                await asyncio.sleep(wait)
                continue
            raise
    logger.error(f"Не удалось отправить сообщение пользователю {user_id} — все {_MAX_RETRIES} попытки исчерпаны")


async def send_message(user_id: int, **kwargs) -> None:
    await _send_with_retry(user_id, **kwargs)


async def send_photo_message(user_id: int, **kwargs) -> None:
    await _send_with_retry(user_id, **kwargs)

redis = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    password=Config.REDIS_PASSWORD or None,
    ssl=Config.REDIS_SSL,
    ssl_ca_certs=Config.REDIS_CA_CERT if Config.REDIS_SSL else None,
    max_connections=200,
)

name_validator = NameValidator(Config.NAMES_FILE_PATH)
cities_client = CitiesClient(
    Config.CITIES_SERVICE_URL,
    Config.CITIES_API_TOKEN,
    verify_tls=Config.CITIES_VERIFY_TLS,
    ca_cert_path=Config.CITIES_CA_CERT,
)
antispam = AntiSpam(redis)


def get_context(user_id: int) -> RedisContext:
    return RedisContext(redis, chat_id=None, user_id=user_id, ttl=Config.REDIS_CONTEXT_TTL)
