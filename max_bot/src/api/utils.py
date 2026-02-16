"""Утилиты для работы с сообщениями и уведомлениями пользователей."""

from sqlalchemy import select
from maxapi.types.input_media import InputMediaBuffer

from core.logger import get_logger
from db.models import Message, MessageStatus, User
from db.session import async_session
from bot.instance import bot
from bot.texts import Texts

logger = get_logger(__name__)


async def send_facade_image(message_id: int, image_bytes: bytes) -> None:
    """
    Отправляет фото фасада пользователю.

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

    # Создаём InputMediaBuffer для отправки фото
    image_media = InputMediaBuffer(buffer=image_bytes, filename="facade.jpg")

    # Отправляем фото пользователю
    await bot.send_message(
        user_id=user.max_id,
        text=Texts.Messages.photo_sent_caption,
        attachments=[image_media],
    )

    # Обновляем статус после успешной отправки фото
    async with async_session() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        msg = result.scalar_one_or_none()
        if msg:
            msg.status = MessageStatus.PHOTO_SENT
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
            await bot.send_message(
                user_id=user.max_id,
                text=Texts.Messages.approved,
            )
        else:
            await bot.send_message(
                user_id=user.max_id,
                text=Texts.Messages.rejected,
            )

    logger.info(f"Модерация сообщения {message_id}: {message.status}")
