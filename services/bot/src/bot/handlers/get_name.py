from maxapi.types import MessageCreated
from maxapi.enums.parse_mode import ParseMode
from maxapi import Bot
from bot.utils import Texts, UserState
from bot.bot import state_machine


async def get_name(event: MessageCreated, bot: Bot) -> None:
    if not event.message or not event.message.from_user:
        return

    # Проверяем что имя не пустое
    if not event.message.text or len(event.message.text) < 1:
        await bot.send_message(
            user_id=event.message.from_user.user_id,
            text=Texts.Messages.invalid_name_text,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    await bot.send_message(
        user_id=event.message.from_user.user_id,
        text=Texts.Messages.add_city_without_geo,
        parse_mode=ParseMode.MARKDOWN,
    )

    # Устанавливаем состояние пользователя на получение города
    await state_machine.set_state(event.message.from_user.user_id, UserState.GET_CITY)
    # Обновляем контекст пользователя: сохраняем имя пользователя
    await state_machine.update_context(
        event.message.from_user.user_id, name=event.message.text.capitalize()
    )


async def get_name_filter(event: MessageCreated) -> bool:
    if not event.message or not event.message.from_user:
        return False
    return (
        await state_machine.get_state(event.message.from_user.user_id)
        == UserState.GET_NAME
    )
