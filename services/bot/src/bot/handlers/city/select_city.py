from aiomax.types.updates import MessageCallbackUpdate
from aiomax import Bot
from aiomax.types import (
    NewMessageBody,
    TextFormat,
    InlineKeyboardAttachmentRequest,
    Keyboard,
    CallbackButton,
    ButtonIntent,
)
from aiomax.methods import AnswerCallback
from bot.utils import Texts, UserState
from bot.bot import state_machine


async def select_city(update: MessageCallbackUpdate, bot: Bot) -> None:
    if update.callback.payload.startswith("select_city:"):
        # Извлекаем название города из payload
        city_name = update.callback.payload.split("select_city:", 1)[1]
        
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.confirm_city.format(city=city_name),
                    format=TextFormat.MARKDOWN,
                    notify=True,
                    attachments=[
                        InlineKeyboardAttachmentRequest(
                            payload=Keyboard(
                                buttons=[
                                    [
                                        CallbackButton(
                                            text="Подтвердить",
                                            payload="confirm_city",
                                            intent=ButtonIntent.POSITIVE,
                                        ),
                                        CallbackButton(
                                            text="Ввести заново",
                                            payload="try_again_city",
                                            intent=ButtonIntent.DEFAULT,
                                        ),
                                    ]
                                ]
                            )
                        )
                    ],
                ),
            )
        )
        
        await state_machine.set_state(
            update.callback.user.user_id, UserState.CONFIRM_CITY
        )
        await state_machine.update_context(
            update.callback.user.user_id, city=city_name
        )


async def select_city_filter(update: MessageCallbackUpdate) -> bool:
    return (
        update.callback.payload.startswith("select_city:")
        and await state_machine.get_state(update.callback.user.user_id)
        == UserState.SELECT_CITY
    )