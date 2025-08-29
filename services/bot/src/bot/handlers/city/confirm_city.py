from maxapi.types import (
    MessageCallback,
    CallbackButton,
    LinkButton,
)
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from bot.utils import Texts, UserState, Config
from bot.bot import state_machine


async def confirm_city(callback: MessageCallback) -> None:
    if callback.payload == "confirm_city":
        # Проверяем, что все необходимые поля заполнены
        message = await state_machine.get_context(
            callback.callback.user.user_id, "message"
        )
        name = await state_machine.get_context(callback.callback.user.user_id, "name")
        city = await state_machine.get_context(callback.callback.user.user_id, "city")

        # Если какое-то из полей пустое, отправляем сообщение об ошибке
        if not message or not name or not city:
            await callback.message.answer(
                text=Texts.Messages.missing_fields,
            )
            return
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            LinkButton(
                text=Texts.Buttons.processing_of_personal_data,
                url=Config.PROCESSING_OF_PERSONAL_DATA_URL,
            )
        )
        keyboard.row(
            CallbackButton(
                text=Texts.Buttons.confirm_fields,
                payload="confirm_fields",
            ),
            CallbackButton(
                text=Texts.Buttons.start_over,
                payload="start_over",
            ),
        )
        
        await callback.message.answer(
            text=Texts.Messages.confirm_fields_with_instruction.format(
                message=message,
                name=name,
                city=city,
            ),
            attachments=[
                keyboard.as_markup()
            ],
        )

        await state_machine.set_state(
            callback.callback.user.user_id, UserState.CONFIRM_FIELDS
        )

    elif callback.payload == "try_again_city":
        # Пользователь хочет ввести город заново
        await callback.message.answer(
            text=Texts.Messages.add_city_without_geo,
        )

        await state_machine.set_state(callback.callback.user.user_id, UserState.GET_CITY)


async def confirm_city_filter(callback: MessageCallback) -> bool:
    current_state = await state_machine.get_state(callback.callback.user.user_id)
    return (
        callback.payload in ("confirm_city", "try_again_city")
        and current_state in (UserState.CONFIRM_CITY, UserState.SELECT_CITY)
    )
