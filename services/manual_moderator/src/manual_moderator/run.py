import asyncio
from .bot import dp, bot, logger
from .utils import UserStorage, Config, Admin
from .handlers import start_router


async def main():
    logger.info("Starting bot...")
    await UserStorage.init(
        Config.REDIS_HOST, Config.REDIS_PORT, Config.REDIS_USER_STORAGE_DB
    )
    await Admin(telegram_id=Config.ADMIN_ID, first_name="Main admin").save()
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(start_router)
    await dp.start_polling(bot, skip_updates=True)


def run():
    asyncio.run(main())
