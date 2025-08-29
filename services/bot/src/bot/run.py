import asyncio
import locale
import logging
from .utils import Config
from .notification_processor import app
from .bot import bot, dispatcher
from shared_models.database import get_tortoise_orm_config
from tortoise import Tortoise


async def main():
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    
    # Регистрируем обработчики событий
    from . import register_handlers
    register_handlers.register_all_handlers(dispatcher)
    
    # Настройка детального логирования HTTP запросов для отладки фантомных апдейтов
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )
    
    # Включить логирование для httpx (используется в aiomax)
    logging.getLogger("httpx").setLevel(logging.DEBUG)
    # Включить логирование для aiomax
    logging.getLogger("aiomax").setLevel(logging.DEBUG)

    await Tortoise.init(
        config=get_tortoise_orm_config(
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
            database=Config.POSTGRES_DB,
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
        )
    )
    await Tortoise.generate_schemas()

    notification_processor_task = asyncio.create_task(app.run())
    
    # Запускаем webhook вместо polling
    try:
        await dispatcher.handle_webhook(
            bot=bot,
            host=Config.WEBHOOK_HOST,
            port=Config.WEBHOOK_PORT,
            log_level='info'
        )
    finally:
        notification_processor_task.cancel()
        await Tortoise.close_connections()


def run():
    asyncio.run(main())