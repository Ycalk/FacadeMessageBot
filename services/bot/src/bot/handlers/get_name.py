from aiomax.types.updates import MessageCreatedUpdate
from aiomax.types import TextFormat
from aiomax import Bot
from aiomax.methods import SendMessage
from bot.utils import Texts, UserState
from bot.bot import state_machine, name_validator


async def get_name(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return

    # Проверяем корректность имени пользователя
    if (
        not update.message.body.text
        or len(update.message.body.text) < 1
        or not await name_validator(update.message.body.text)
    ):
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.invalid_name_text,
                text_format=TextFormat.MARKDOWN,
            )
        )
        return

    await bot(
        SendMessage(
            user_id=update.message.sender.user_id,
            text=Texts.Messages.add_city_without_geo,
            text_format=TextFormat.MARKDOWN,
        )
    )

    # Устанавливаем состояние пользователя на получение города
    await state_machine.set_state(update.message.sender.user_id, UserState.GET_CITY)
    # Обновляем контекст пользователя: сохраняем имя пользователя
    await state_machine.update_context(
        update.message.sender.user_id, name=update.message.body.text.capitalize()
    )


async def get_name_filter(update: MessageCreatedUpdate) -> bool:
    if not update.message or not update.message.sender:
        return False
    return (
        await state_machine.get_state(update.message.sender.user_id)
        == UserState.GET_NAME
    )
