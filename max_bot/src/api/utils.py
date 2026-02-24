"""Утилиты для работы с сообщениями и уведомлениями пользователей."""

import httpx
from sqlalchemy import select
from maxapi.types.input_media import InputMediaBuffer
from maxapi.types import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from core.logger import get_logger
from db.models import Message, MessageStatus, User
from db.session import async_session
from bot.instance import send_message, send_photo_message
from bot.texts import Texts

logger = get_logger(__name__)


async def send_facade_image(message_id: int, image_bytes: bytes) -> None:
    """
    Отправляет фото фасада пользователю, если он дал согласие на получение фото.

    Args:
        message_id: ID сообщения в БД
        image_bytes: Байты изображения для отправки

    Raises:
        ValueError: Если сообщение не найдено
    """
    # Получаем сообщение и пользователя
    async with async_session() as session:
        result = await session.execute(
            select(Message, User)
            .join(User, Message.user_id == User.id)
            .where(Message.id == message_id)
        )
        row = result.one_or_none()

        if not row:
            raise ValueError(f"Сообщение {message_id} не найдено")

        message, user = row

    if message.status != MessageStatus.APPROVED:
        logger.warning(
            f"Игнорируем отправку фото для сообщения {message_id}: "
            f"статус {message.status} не прошёл модерацию"
        )
        return

    # Факт показа фиксируем независимо от желания получить фото.
    async with async_session() as session:
        result = await session.execute(select(Message).where(Message.id == message_id))
        msg = result.scalar_one_or_none()
        if msg and not msg.shown_on_facade:
            msg.shown_on_facade = True
            await session.commit()

    # Проверяем, хочет ли пользователь получить фото (False = явный отказ)
    if message.want_photo is False:
        logger.info(
            f"Пользователь отказался от фото для сообщения {message_id}, "
            "фиксируем только shown_on_facade"
        )
        return

    # Создаём InputMediaBuffer для отправки фото
    image_media = InputMediaBuffer(buffer=image_bytes, filename="facade.jpg")

    # Отправляем фото пользователю (строгий лимит для тяжёлых вложений)
    await send_photo_message(
        user_id=user.max_id,
        text=Texts.Messages.photo_sent_caption,
        attachments=[image_media],
    )

    # Обновляем факт отправки фото после успешной отправки
    async with async_session() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        msg = result.scalar_one_or_none()
        if msg:
            msg.photo_sent = True
            await session.commit()

    logger.info(f"Фото фасада отправлено пользователю {user.max_id} для сообщения {message_id}")


async def notify_user_moderation_result(message_id: int, approved: bool) -> None:
    """
    Уведомляет пользователя о результате модерации.

    Args:
        message_id: ID сообщения в БД
        approved: True если одобрено, False если отклонено

    Raises:
        ValueError: Если сообщение не найдено
    """
    async with async_session() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()

        if not message:
            raise ValueError(f"Сообщение {message_id} не найдено")

        # Обновляем статус
        message.status = MessageStatus.APPROVED if approved else MessageStatus.REJECTED
        await session.commit()
        await session.refresh(message)

        # Получаем пользователя для отправки уведомления
        user_result = await session.execute(
            select(User).where(User.id == message.user_id)
        )
        user = user_result.scalar_one_or_none()

    if user:
        if approved:
            text = Texts.Messages.approved

            keyboard = InlineKeyboardBuilder()
            keyboard.add(
                CallbackButton(
                    text=Texts.Buttons.yes_photo,
                    payload=f"want_photo_yes_{message_id}",
                )
            )
            keyboard.add(
                CallbackButton(
                    text=Texts.Buttons.no_photo,
                    payload=f"want_photo_no_{message_id}",
                )
            )

            # Пробуем приложить превью сообщения на фоне
            preview_image: InputMediaBuffer | None = None
            if message.preview_url:
                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        resp = await client.get(message.preview_url)
                        resp.raise_for_status()
                        preview_image = InputMediaBuffer(
                            buffer=resp.content, filename="preview.jpg"
                        )
                except Exception as e:
                    logger.warning(
                        f"Не удалось загрузить превью для сообщения {message_id}: {e}"
                    )

            if preview_image:
                await send_photo_message(
                    user_id=user.max_id,
                    text=text,
                    attachments=[preview_image, keyboard.as_markup()],
                )
            else:
                await send_message(
                    user_id=user.max_id,
                    text=text,
                    attachments=[keyboard.as_markup()],
                )
        else:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(
                CallbackButton(
                    text=Texts.Buttons.send_message,
                    payload="send_message",
                )
            )
            await send_message(
                user_id=user.max_id,
                text=Texts.Messages.rejected,
                attachments=[keyboard.as_markup()],
            )

    logger.info(f"Модерация сообщения {message_id}: {message.status}")


async def send_rejection_notification(message_id: int) -> None:
    """
    Отправляет пользователю уведомление об отклонении сообщения.

    Args:
        message_id: ID сообщения в БД
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Message, User)
                .join(User, Message.user_id == User.id)
                .where(Message.id == message_id)
            )
            row = result.one_or_none()

            if not row:
                logger.error(f"Сообщение {message_id} не найдено для отправки уведомления об отклонении")
                return

            message, user = row

        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            CallbackButton(
                text=Texts.Buttons.send_message,
                payload="send_message",
            )
        )
        await send_message(
            user_id=user.max_id,
            text=Texts.Messages.rejected,
            attachments=[keyboard.as_markup()],
        )
        logger.info(f"Уведомление об отклонении отправлено пользователю {user.max_id} для сообщения {message_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления об отклонении для сообщения {message_id}: {e}")
