from maxapi.types import MessageCallback, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from bot.utils import Texts, UserState
from bot.bot import state_machine


async def select_city(callback: MessageCallback) -> None:
    if callback.payload.startswith("select_city:"):
        # Извлекаем название города из payload
        city_name = callback.payload.split("select_city:", 1)[1]
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            CallbackButton(
                text="Подтвердить",
                payload="confirm_city",
            ),
            CallbackButton(
                text="Ввести заново",
                payload="try_again_city",
            ),
        )
        
        await callback.message.answer(
            text=Texts.Messages.confirm_city.format(city=city_name),
            attachments=[keyboard.as_markup()],
        )
        
        await state_machine.set_state(
            callback.from_user.user_id, UserState.CONFIRM_CITY
        )
        await state_machine.update_context(
            callback.from_user.user_id, city=city_name
        )


async def select_city_filter(callback: MessageCallback) -> bool:
    return (
        callback.payload.startswith("select_city:")
        and await state_machine.get_state(callback.from_user.user_id)
        == UserState.SELECT_CITY
    )