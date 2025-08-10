import asyncio
from .bot import dp, bot, logger
from .utils import UserStorage, Config, Admin, BotData
from .handlers import (
    start_router,
    admin_router,
    moderator_commands_router,
    moderator_moderate_result_router,
)
from .utils import ModerationLoop
from .notification_processor import app, broker


async def main():
    logger.info("Starting bot...")
    await UserStorage.init(
        Config.REDIS_HOST, Config.REDIS_PORT, Config.REDIS_USER_STORAGE_DB, broker
    )
    if not await Admin.exists(telegram_id=Config.MAIN_ADMIN_ID):
        await Admin(telegram_id=Config.MAIN_ADMIN_ID, first_name="Main admin").save()
    await BotData.disable_auto_approve()
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(moderator_commands_router)
    dp.include_router(moderator_moderate_result_router)

    moderation_loop_task = asyncio.create_task(ModerationLoop(bot).start())
    dp_task = asyncio.create_task(dp.start_polling(bot, skip_updates=True))
    notification_processor_task = asyncio.create_task(app.run())

    await notification_processor_task

    moderation_loop_task.cancel()
    dp_task.cancel()
    notification_processor_task.cancel()


def run():
    asyncio.run(main())
