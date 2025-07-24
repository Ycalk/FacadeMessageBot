import asyncio
from .handlers import start_handler, confirm_start, confirm_start_filter
from .bot import bot


async def main():
    bot.register_handler(start_handler)
    bot.register_handler(confirm_start, filter=confirm_start_filter)
    await bot.start_polling()


def run():
    asyncio.run(main())
