import asyncio
from .handlers import (
    start_handler,
    confirm_start,
    confirm_start_filter,
    get_message,
    get_message_filter,
    add_name_solution,
    add_name_solution_filter,
    get_name,
    get_name_filter,
    add_city_solution,
    add_city_solution_filter,
    get_city,
    get_city_filter,
)
from .bot import bot


async def main():
    bot.register_handler(start_handler)
    bot.register_handler(confirm_start, filter=confirm_start_filter)
    bot.register_handler(get_message, filter=get_message_filter)
    bot.register_handler(add_name_solution, filter=add_name_solution_filter)
    bot.register_handler(get_name, filter=get_name_filter)
    bot.register_handler(add_city_solution, filter=add_city_solution_filter)
    bot.register_handler(get_city, filter=get_city_filter)
    await bot.start_polling()


def run():
    asyncio.run(main())
