import logging
from aiomax.types.updates import MessageCallbackUpdate
from aiomax.types import (
    NewMessageBody,
    TextFormat,
    InlineKeyboardAttachmentRequest,
    Keyboard,
    CallbackButton,
    ButtonIntent,
)
from aiomax.methods import AnswerCallback, SendMessage
from aiomax import Bot
from bot.utils import Texts, UserState
from bot.bot import state_machine
from shared_models.database import Message, User
from shared_models.enums import MessageState
from bot.notification_processor.app import broker
from shared_models.messaging import (
    auto_moderator_queue,
    moderator_exchange,
    MessageInput,
)
from shared_models.messaging import Message as MessageSharedModel


logger = logging.getLogger(__name__)


async def confirm_fields(update: MessageCallbackUpdate, bot: Bot) -> None:
    if update.callback.payload == "start_over":
        # Пользователь хочет начать заново,
        # сбрасываем контекст и устанавливаем состояние на ввод сообщения
        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.get_message,
                    attachments=[],
                    notify=True,
                    format=TextFormat.MARKDOWN,
                ),
            )
        )
        await state_machine.set_state(
            update.callback.user.user_id, UserState.GET_MESSAGE
        )
        await state_machine.clear_context(update.callback.user.user_id)

    elif update.callback.payload == "confirm_fields":
        user = await User.get_or_none(max_id=update.callback.user.user_id)
        message = await state_machine.get_context(
            update.callback.user.user_id, "message"
        )
        name = await state_machine.get_context(update.callback.user.user_id, "name")
        city = await state_machine.get_context(update.callback.user.user_id, "city")

        if not message or not name or not city or not user:
            # Если какое-то из полей пустое, отправляем сообщение об ошибке
            await bot(
                AnswerCallback(
                    callback_id=update.callback.callback_id,
                    message=NewMessageBody(
                        text=Texts.Messages.missing_fields,
                        attachments=[],
                        notify=True,
                        format=TextFormat.MARKDOWN,
                    ),
                )
            )
            return

        await bot(
            AnswerCallback(
                callback_id=update.callback.callback_id,
                message=NewMessageBody(
                    text=Texts.Messages.confirm_fields.format(
                        message=message,
                        name=name,
                        city=city,
                    ),
                    attachments=[],
                    notify=True,
                    format=TextFormat.MARKDOWN,
                ),
            )
        )
        await bot(
            SendMessage(
                user_id=update.callback.user.user_id,
                text=Texts.Messages.start_moderation,
                attachments=[
                    InlineKeyboardAttachmentRequest(
                        payload=Keyboard(
                            buttons=[
                                [
                                    CallbackButton(
                                        text=Texts.Buttons.new_message,
                                        payload="new_message",
                                        intent=ButtonIntent.POSITIVE,
                                    )
                                ],
                            ],
                        )
                    )
                ],
            )
        )

        # Создаем новое сообщение с подтвержденными полями
        new_message = await Message.create(
            user=user,
            text=message,
            name=name,
            city=city,
            send_photo=True,
            state=MessageState.PENDING_AUTO_MODERATION,
        )

        # Отправляем новое сообщение в очередь авто-модерации
        await broker.publish(
            MessageInput(
                message=MessageSharedModel(
                    message_id=new_message.id,
                    text=new_message.text,
                    city=new_message.city,
                    name=new_message.name,
                    send_photo=new_message.send_photo,
                )
            ),
            auto_moderator_queue,
            moderator_exchange,
        )


async def confirm_fields_filter(update: MessageCallbackUpdate) -> bool:
    user_id = update.callback.user.user_id
    payload = update.callback.payload
    
    # Базовые проверки
    if payload not in ("confirm_fields", "start_over"):
        return False
    
    current_state = await state_machine.get_state(user_id)
    if current_state != UserState.CONFIRM_FIELDS:
        return False
    
    # Для кнопки "start_over" не проверяем дубликаты (пользователь хочет начать заново)
    if payload == "start_over":
        return True
    
    # Проверяем что пользователь не отправлял уже это сообщение на модерацию
    try:
        user = await User.get_or_none(max_id=user_id)
        
        if user:
            # Получаем контекст пользователя с данными сообщения
            message_text = await state_machine.get_context(user_id, "message")
            name = await state_machine.get_context(user_id, "name")
            city = await state_machine.get_context(user_id, "city")
            
            if message_text and name and city:
                # Проверяем есть ли уже сообщение с такими же данными в процессе обработки
                existing_message = await Message.filter(
                    user=user,
                    text=message_text,
                    name=name,
                    city=city,
                ).first()
                
                if existing_message:
                    return False  # Дубликат уже в обработке, не обрабатываем
            
    except Exception as e:
        logger.error(f"ОШИБКА при проверке дубликатов: {e}")
    
    return True
