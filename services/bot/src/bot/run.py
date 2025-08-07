import asyncio

from .utils import Config
from .notification_processor import app
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
    confirm_fields,
    confirm_fields_filter,
    create_command_filter,
    create_command_handler,
    message_command_filter,
    message_command_handler,
    new_message,
    new_message_filter,
)
from .bot import bot
from shared_models.database import get_tortoise_orm_config
from tortoise import Tortoise


async def main():
    bot.register_handler(create_command_handler, filter=create_command_filter)
    bot.register_handler(message_command_handler, filter=message_command_filter)
    bot.register_handler(start_handler)
    bot.register_handler(confirm_start, filter=confirm_start_filter)
    bot.register_handler(get_message, filter=get_message_filter)
    bot.register_handler(add_name_solution, filter=add_name_solution_filter)
    bot.register_handler(get_name, filter=get_name_filter)
    bot.register_handler(add_city_solution, filter=add_city_solution_filter)
    bot.register_handler(get_city, filter=get_city_filter)
    bot.register_handler(confirm_city, filter=confirm_city_filter)
    bot.register_handler(get_photo_solution, filter=get_photo_solution_filter)
    bot.register_handler(confirm_fields, filter=confirm_fields_filter)
    bot.register_handler(new_message, filter=new_message_filter)

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
    polling_task = asyncio.create_task(bot.start_polling())

    await notification_processor_task

    polling_task.cancel()
    notification_processor_task.cancel()
    await Tortoise.close_connections()


def run():
    asyncio.run(main())
