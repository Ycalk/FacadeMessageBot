import asyncio

from .utils import Config
from .notification_processor import app
from .handlers import (
    start_handler,
    confirm_terms_of_use,
    confirm_terms_of_use_filter,
    send_message_handler,
    send_message_filter,
    write_message_handler,
    write_message_filter,
    get_message,
    get_message_filter,
    get_name,
    get_name_filter,
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
    new_message,
    new_message_filter,
    stop_handler,
)
from .bot import bot
from shared_models.database import get_tortoise_orm_config
from tortoise import Tortoise


async def main():
    bot.register_handler(create_command_handler, filter=create_command_filter)
    bot.register_handler(start_handler)
    bot.register_handler(stop_handler)
    bot.register_handler(confirm_terms_of_use, filter=confirm_terms_of_use_filter)
    bot.register_handler(send_message_handler, filter=send_message_filter)
    bot.register_handler(write_message_handler, filter=write_message_filter)
    bot.register_handler(get_message, filter=get_message_filter)
    bot.register_handler(get_name, filter=get_name_filter)
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
