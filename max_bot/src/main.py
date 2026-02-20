import asyncio

from bot.instance import bot, dispatcher
from bot.routers import (
    system_router,
    callbacks_router,
    text_router,
)
from db.models import Base
from db.session import engine
from api.app import create_app
from core.config import Config
from core.logger import get_logger
from services.app_settings import init_default_settings
from services.auto_moderator import recover_stuck_messages
from services.blacklist import load_blacklist

logger = get_logger(__name__)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы БД созданы")


async def setup_webhook() -> None:
    """Подписывает бота на вебхук."""
    await bot.delete_webhook()
    result = await bot.subscribe_webhook(
        url=Config.BOT_WEBHOOK_URL,
        secret=Config.BOT_WEBHOOK_SECRET or None,
    )
    logger.info(f"Вебхук установлен: {Config.BOT_WEBHOOK_URL} → {result}")


async def main() -> None:
    await init_db()

    logger.info("Инициализация настроек по умолчанию...")
    await init_default_settings()

    logger.info("Загрузка чёрного списка слов...")
    await load_blacklist()

    logger.info("Проверка зависших сообщений...")
    await recover_stuck_messages()

    dispatcher.include_routers(
        system_router,
        callbacks_router,
        text_router,
    )

    # Подписываем бота на вебхук (Max API будет слать POST на BOT_WEBHOOK_URL)
    await setup_webhook()

    dispatcher.webhook_app = create_app()

    logger.info(f"Запуск сервера на {Config.WEBHOOK_HOST}:{Config.WEBHOOK_PORT}")
    await dispatcher.handle_webhook(
        bot=bot,
        host=Config.WEBHOOK_HOST,
        port=Config.WEBHOOK_PORT,
    )


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
