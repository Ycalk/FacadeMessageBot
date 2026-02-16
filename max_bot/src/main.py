import asyncio
import uvicorn

from bot.instance import bot, dispatcher
from bot.routers import (
    system_router,
    callbacks_router,
    text_router,
)
from db.models import Base
from db.session import engine
from api.app import create_webhook_app
from core.config import Config
from core.logger import get_logger
from services.auto_moderator import recover_stuck_messages

logger = get_logger(__name__)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы БД созданы")


async def run_webhook_server(app) -> None:
    """Запускает FastAPI сервер для приёма webhooks от Moder Service."""
    config = uvicorn.Config(
        app,
        host=Config.WEBHOOK_HOST,
        port=Config.WEBHOOK_PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    await init_db()

    # Восстанавливаем зависшие сообщения после перезагрузки
    logger.info("Проверка зависших сообщений...")
    await recover_stuck_messages()

    dispatcher.include_routers(
        system_router,
        callbacks_router,
        text_router,
    )

    # Запускаем webhook сервер в фоне
    webhook_app = create_webhook_app()
    webhook_task = asyncio.create_task(run_webhook_server(webhook_app))

    logger.info("Запуск Max бота в режиме polling...")
    try:
        await dispatcher.start_polling(bot)
    finally:
        webhook_task.cancel()


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
