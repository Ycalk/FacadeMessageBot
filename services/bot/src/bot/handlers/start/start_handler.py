from maxapi.types import BotStarted, MessageCreated, InputFile, UploadType
from maxapi.types import ImageAttachmentRequest, PhotoAttachmentRequestPayload
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder, CallbackButton, LinkButton
from maxapi.enums.parse_mode import ParseMode
from maxapi import Bot
from bot.utils import Texts, Config
from typing import Union
import os


async def start_handler(event: Union[BotStarted, MessageCreated], bot: Bot) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        LinkButton(
            text=Texts.Buttons.terms_of_use,
            url=Config.TERMS_OF_USE_URL,
        )
    )
    keyboard.row()
    keyboard.add(
        CallbackButton(
            text=Texts.Buttons.send_message,
            payload="send_message",
        )
    )
    
    attachments = [keyboard.as_markup()]
    
    # Добавляем test.png изображение
    test_image_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'test.png')
    if os.path.exists(test_image_path):
        try:
            with open(test_image_path, 'rb') as f:
                image_data = f.read()
            
            input_file = InputFile(
                data=image_data,
                filename='test.png',
                upload_type=UploadType.IMAGE
            )
            
            # Загружаем изображение и получаем токен
            image_token = await bot.upload(input_file)
            if image_token:
                image_attachment = ImageAttachmentRequest(
                    payload=PhotoAttachmentRequestPayload(
                        token=image_token
                    )
                )
                attachments.append(image_attachment)
        except Exception as e:
            # В случае ошибки просто продолжаем без изображения
            print(f"Ошибка загрузки изображения: {e}")

    await bot.send_message(
        user_id=event.user.user_id if hasattr(event, 'user') else event.message.sender.user_id,
        text=Texts.Messages.start,
        parse_mode=ParseMode.MARKDOWN,
        attachments=attachments,
    )
