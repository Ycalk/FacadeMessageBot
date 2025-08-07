import asyncio
from .bot import dp, bot, logger
from .utils import UserStorage, Config, Admin, BotData
from .handlers import start_router, admin_router, moderator_commands_router


async def main():
    logger.info("Starting bot...")
    await UserStorage.init(
        Config.REDIS_HOST, Config.REDIS_PORT, Config.REDIS_USER_STORAGE_DB
    )
    if not await Admin.exists(telegram_id=Config.MAIN_ADMIN_ID):
        await Admin(telegram_id=Config.MAIN_ADMIN_ID, first_name="Main admin").save()
    await BotData.disable_auto_approve()
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(moderator_commands_router)
    await dp.start_polling(bot, skip_updates=True)


def run():
    asyncio.run(main())
