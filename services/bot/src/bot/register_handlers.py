import logging
from maxapi import Dispatcher, F
from bot.bot import state_machine
from bot.utils import UserState

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
        send_message_handler
    )
    
    # Обработчик команды /create
    @dp.message_created(F.message.body.text == "/create")
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
        logger.debug(f"Callback send_message от пользователя {event.callback.user.user_id}")
        await send_message_handler(event)
    
    @dp.message_callback(F.callback.payload.startswith("select_city_"))
    async def _(event):
        logger.debug(f"Callback select_city от пользователя {event.callback.user.user_id}, payload: {event.callback.payload}")
        await select_city(event)
    
    @dp.message_callback(F.callback.payload in ["confirm_city", "try_again_city"])
    async def _(event):
        logger.debug(f"Callback confirm_city от пользователя {event.callback.user.user_id}")
        await confirm_city(event)
    
    @dp.message_callback(F.callback.payload.startswith("accept_get_photo") | F.callback.payload.startswith("reject_get_photo"))
    async def _(event):
        logger.debug(f"Callback photo solution от пользователя {event.callback.user.user_id}, payload: {event.callback.payload}")
        await get_photo_solution(event)
    
    @dp.message_callback(F.callback.payload.in_(["confirm_fields", "edit_fields", "start_over"]))
    async def _(event):
        logger.debug(f"Callback confirm/edit fields от пользователя {event.callback.user.user_id}, payload: {event.callback.payload}")
        await confirm_fields(event)
    
    # Обработчики сообщений - проверка состояния происходит внутри handler'ов через фильтры  
    @dp.message_created(F.message.body.text)  # Любое текстовое сообщение
    async def _(event):
        current_state = await state_machine.get_state(event.message.sender.user_id)
        logger.debug(f"Обработчик текстовых сообщений: пользователь {event.message.sender.user_id}, текст: '{event.message.body.text}', состояние: {current_state}")
        
        # Выбираем обработчик в зависимости от состояния пользователя
        if current_state == UserState.GET_MESSAGE:
            await get_message(event, event.bot)
        elif current_state == UserState.GET_NAME:
            await get_name(event, event.bot)
        elif current_state == UserState.GET_CITY:
            await get_city(event, event.bot)
        else:
            logger.debug(f"Неожиданное состояние {current_state} для пользователя {event.message.sender.user_id}, игнорируем сообщение")