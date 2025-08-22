import asyncio
import logging
from .utils import UpdateLoop
from .app import (
    app,
    facade_message_publisher,
    bot_publisher,
    sheet,
    storage,
)


async def main():
    app_task = asyncio.create_task(app.run())
    await sheet.initialize()
    update_loop = UpdateLoop(
        sheet=sheet,
        storage=storage,
        logger=logging.getLogger("faststream"),
        facade_message_publisher=facade_message_publisher,
        bot_publisher=bot_publisher,
    )
    update_loop_task = asyncio.create_task(update_loop.start())
    await app_task

    update_loop_task.cancel()


def run():
    asyncio.run(main())
