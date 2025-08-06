import logging
from aiogram import Bot, Dispatcher
from .utils import Config
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from redis.asyncio.client import Redis
from aiogram.fsm.storage.redis import RedisStorage


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=Config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher(
    storage=RedisStorage(
        redis=Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_FSM_STORAGE_DB,
        )
    ),
    bot=bot,
)
redis = Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_USER_STORAGE_DB,
)
