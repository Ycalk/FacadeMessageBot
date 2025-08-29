import logging
from maxapi import Dispatcher, F

logger = logging.getLogger(__name__)


def register_all_handlers(dp: Dispatcher) -> None:
    """Регистрация всех обработчиков событий бота"""
    from .handlers import (
        start_handler,
        get_message,
        get_name,
        get_city,
        select_city,
        confirm_city,
        get_photo_solution,
        confirm_fields,
        create_command_handler,
        stop_handler,
    )
    
    # Обработчик команды /create
    @dp.message_created(F.message.text == "/create")
    async def _(event):
        logger.debug(f"Получена команда /create от пользователя {event.message.sender.user_id}")
        await create_command_handler(event, event.bot)
    
    # Обработчик команды /start
    @dp.bot_started()
    async def _(event):
        logger.debug(f"Bot started для пользователя {event.user.user_id}")
        await start_handler(event, event.bot)
    
    # Обработчик команды /stop
    @dp.bot_stopped()
    async def _(event):
        logger.debug(f"Bot stopped для пользователя {event.user.user_id}")
        await stop_handler(event, event.bot)
    
    # Callback обработчики
    @dp.message_callback(F.callback.payload == "send_message")
    async def _(event):
        logger.debug(f"Callback send_message от пользователя {event.callback.sender.user_id}")
        await create_command_handler(event, event.bot)
    
    @dp.message_callback(F.callback.payload.startswith("select_city_"))
    async def _(event):
        logger.debug(f"Callback select_city от пользователя {event.callback.sender.user_id}, payload: {event.callback.payload}")
        await select_city(event)
    
    @dp.message_callback(F.callback.payload == "confirm_city")
    async def _(event):
        logger.debug(f"Callback confirm_city от пользователя {event.callback.sender.user_id}")
        await confirm_city(event)
    
    @dp.message_callback(F.callback.payload.startswith("accept_get_photo") | F.callback.payload.startswith("reject_get_photo"))
    async def _(event):
        logger.debug(f"Callback photo solution от пользователя {event.callback.sender.user_id}, payload: {event.callback.payload}")
        await get_photo_solution(event)
    
    @dp.message_callback(F.callback.payload.in_(["confirm_fields", "edit_fields"]))
    async def _(event):
        logger.debug(f"Callback confirm/edit fields от пользователя {event.callback.sender.user_id}, payload: {event.callback.payload}")
        await confirm_fields(event)
    
    # Обработчики сообщений - проверка состояния происходит внутри handler'ов через фильтры
    @dp.message_created(F.message.text)  # Любое текстовое сообщение
    async def _(event):
        logger.debug(f"Получено текстовое сообщение от пользователя {event.message.sender.user_id}: '{event.message.text}'")
        # Обработчики сами проверяют состояния и решают, обрабатывать ли событие
        await get_message(event, event.bot)
        await get_name(event, event.bot) 
        await get_city(event, event.bot)