import asyncio
from .bot import bot, broker
from .handlers import message, start


async def main():
    bot.register_handler(message)
    bot.register_handler(start)

    await broker.start()
    await bot.start_polling()


def run():
    asyncio.run(main())
