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
from bot.utils import Texts, UserState
from bot.bot import state_machine, city_extractor, cities_client


async def get_city(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender:
        return

    # Проверяем, что пользователь отправил сообщение с вложением локации
    # Если вложение есть, значит пользователь нажал "Определить автоматически"
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
            await state_machine.set_state(
                update.message.sender.user_id, UserState.CONFIRM_CITY
            )
            await state_machine.update_context(update.message.sender.user_id, city=city)
        return

    # Если вложения нет, значит пользователь ввел текстовое сообщение
    # Проверяем, что текст сообщения не пустой
    bot.logger.info("User input city: " + str(update.message.body.text))
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
        # Ищем города в cities service
        search_result = await cities_client.search_cities(
            update.message.body.text, limit=5
        )
        bot.logger.info("Search result" + str(search_result))
        if search_result and search_result.cities:
            # Если найдены точные совпадения, предлагаем их как варианты
            if len(search_result.cities) == 1:
                # Один точный результат - сразу предлагаем подтвердить
                city = search_result.cities[0].name
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
                await state_machine.set_state(
                    update.message.sender.user_id, UserState.CONFIRM_CITY
                )
                await state_machine.update_context(
                    update.message.sender.user_id, city=city
                )
            else:
                # Несколько результатов - показываем варианты
                buttons = []
                for city in search_result.cities[:4]:  # Максимум 4 варианта
                    buttons.append(
                        [
                            CallbackButton(
                                text=city.name,
                                payload=f"select_city:{city.name}",
                                intent=ButtonIntent.DEFAULT,
                            )
                        ]
                    )

                buttons.append(
                    [
                        CallbackButton(
                            text="Ввести заново",
                            payload="try_again_city",
                            intent=ButtonIntent.DEFAULT,
                        )
                    ]
                )

                cities_list = "\n".join(
                    [f"• {city.name}" for city in search_result.cities[:4]]
                )
                await bot(
                    SendMessage(
                        user_id=update.message.sender.user_id,
                        text=f"Найдены следующие города:\n{cities_list}\n\nВыберите подходящий:",
                        text_format=TextFormat.MARKDOWN,
                        attachments=[
                            InlineKeyboardAttachmentRequest(
                                payload=Keyboard(buttons=buttons)
                            )
                        ],
                    )
                )
                await state_machine.set_state(
                    update.message.sender.user_id, UserState.SELECT_CITY
                )
        else:
            # Если cities service не доступен или не найдено совпадений, используем старую логику
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
            await state_machine.set_state(
                update.message.sender.user_id, UserState.CONFIRM_CITY
            )
            await state_machine.update_context(update.message.sender.user_id, city=city)


async def get_city_filter(update: MessageCreatedUpdate) -> bool:
    if not update.message or not update.message.sender:
        return False
    return (
        await state_machine.get_state(update.message.sender.user_id)
        == UserState.GET_CITY
    )
