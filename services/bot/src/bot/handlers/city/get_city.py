from aiomax.types.updates import MessageCreatedUpdate
from aiomax.types import (
    InlineKeyboardAttachmentRequest,
    TextFormat,
    Keyboard,
    CallbackButton,
    ButtonIntent,
    LocationAttachment,
)
from aiomax import Bot
from aiomax.methods import SendMessage
from ...utils import Texts, UserState
from ...bot import state_machine, city_extractor


async def get_city(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return
    if (
        update.message.body.attachments
        and len(update.message.body.attachments) == 1
        and isinstance(update.message.body.attachments[0], LocationAttachment)
    ):
        location_attachment: LocationAttachment = update.message.body.attachments[0]
        city = await city_extractor.extract_from_coordinates(
            location_attachment.latitude, location_attachment.longitude
        )
        if not city:
            await bot(
                SendMessage(
                    user_id=update.message.sender.user_id,
                    text=Texts.Messages.location_not_found,
                    text_format=TextFormat.MARKDOWN,
                )
            )
        else:
            await bot(
                SendMessage(
                    user_id=update.message.sender.user_id,
                    text=Texts.Messages.confirm_city.format(city=city),
                    text_format=TextFormat.MARKDOWN,
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
                                            text="Ввести вручную",
                                            payload="write_city",
                                            intent=ButtonIntent.DEFAULT,
                                        ),
                                    ]
                                ]
                            )
                        )
                    ],
                )
            )
        state_machine.set_state(update.message.sender.user_id, UserState.CONFIRM_CITY)
        state_machine.update_context(update.message.sender.user_id, city=city)
        return

    if not update.message.body.text:
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.city_not_found,
                text_format=TextFormat.MARKDOWN,
            )
        )
        return
    else:
        city = city_extractor.extract_from_text(update.message.body.text)
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text=Texts.Messages.confirm_city.format(city=city),
                text_format=TextFormat.MARKDOWN,
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
            )
        )
        state_machine.set_state(update.message.sender.user_id, UserState.CONFIRM_CITY)
        state_machine.update_context(update.message.sender.user_id, city=city)


def get_city_filter(update: MessageCreatedUpdate) -> bool:
    if not update.message or not update.message.sender:
        return False
    return state_machine.get_state(update.message.sender.user_id) == UserState.GET_CITY
