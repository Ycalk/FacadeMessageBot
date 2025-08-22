import asyncio
from .utils import UpdateLoop, Sheet
from .app import app, startup_complete_event, facade_message_publisher, bot_publisher
from faststream import context


async def main():
    app_task = asyncio.create_task(app.run())
    try:
        await asyncio.wait_for(startup_complete_event.wait(), timeout=5)
    except asyncio.TimeoutError:
        print("App failed to start within 5 seconds.")
        app_task.cancel()
        return
    sheet: Sheet = context.get("sheet")
    await sheet.initialize()
    update_loop = UpdateLoop(
        sheet=sheet,
        storage=context.get("storage"),
        logger=context.get("logger"),
        facade_message_publisher=facade_message_publisher,
        bot_publisher=bot_publisher,
    )
    update_loop_task = asyncio.create_task(update_loop.start())
    await app_task

    update_loop_task.cancel()


def run():
    asyncio.run(main())
