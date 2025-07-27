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
    confirm_city,
    confirm_city_filter,
    get_photo_solution,
    get_photo_solution_filter,
    set_date,
    set_date_filter,
    set_time,
    set_time_filter,
    confirm_fields,
    confirm_fields_filter,
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
    bot.register_handler(confirm_city, filter=confirm_city_filter)
    bot.register_handler(get_photo_solution, filter=get_photo_solution_filter)
    bot.register_handler(set_date, filter=set_date_filter)
    bot.register_handler(set_time, filter=set_time_filter)
    bot.register_handler(confirm_fields, filter=confirm_fields_filter)
    await bot.start_polling()


def run():
    asyncio.run(main())
