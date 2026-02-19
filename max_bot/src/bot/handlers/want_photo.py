"""Обработчики выбора пользователя — получать ли фото с фасада."""

from core.logger import get_logger

from maxapi.types import MessageCallback
from sqlalchemy import select

from bot.texts import Texts
from db.models import Message
from db.session import async_session

logger = get_logger(__name__)


async def want_photo_yes_handler(callback: MessageCallback) -> None:
    """Пользователь хочет получить фото — сохраняем предпочтение."""
    payload = callback.callback.payload
    try:
        message_id = int(payload.split("_")[-1])
    except (ValueError, IndexError):
        logger.error(f"Некорректный payload для want_photo_yes: {payload}")
        return

    async with async_session() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        if not message:
            return
        if message.want_photo is not None:
            logger.info(f"Повторное нажатие want_photo_yes для сообщения {message_id}, игнорируем")
            return
        message.want_photo = True
        await session.commit()
        logger.info(f"Пользователь согласился на фото для сообщения {message_id}")

    await callback.message.answer(text=Texts.Messages.photo_yes_response)


async def want_photo_no_handler(callback: MessageCallback) -> None:
    """Пользователь не хочет фото — сохраняем предпочтение."""
    payload = callback.callback.payload
    try:
        message_id = int(payload.split("_")[-1])
    except (ValueError, IndexError):
        logger.error(f"Некорректный payload для want_photo_no: {payload}")
        return

    async with async_session() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        if not message:
            return
        if message.want_photo is not None:
            logger.info(f"Повторное нажатие want_photo_no для сообщения {message_id}, игнорируем")
            return
        message.want_photo = False
        await session.commit()
        logger.info(f"Пользователь отказался от фото для сообщения {message_id}")

    await callback.message.answer(text=Texts.Messages.photo_no_response)
