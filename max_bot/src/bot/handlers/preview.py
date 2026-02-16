"""Обработчик предпросмотра и отправки на модерацию."""

import asyncio
from datetime import datetime, timedelta

from maxapi.types import MessageCallback, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func
from core.logger import get_logger

from bot.instance import get_context
from bot.states import UserStates
from bot.texts import Texts
from bot.handlers.wrong_step import reply_wrong_step_for_callback
from core.config import Config
from db.models import Message, User, MessageStatus
from db.session import async_session
from services.auto_moderator import auto_moderate_message

logger = get_logger(__name__)


async def send_to_moderation(callback: MessageCallback) -> None:
    """Отправка сообщения на модерацию."""
    user_id = callback.callback.user.user_id
    payload = callback.callback.payload
    ctx = get_context(user_id)
    current_state = await ctx.get_state()

    if current_state != str(UserStates.preview):
        await reply_wrong_step_for_callback(callback)
        return

    if payload != 'send_to_moderation':
        return

    # Получаем все данные
    data = await ctx.get_data()
    message_text = data.get("message")
    name = data.get("name")
    city = data.get("city")
    frame_id_raw = data.get("frame_id")

    if not all([message_text, name, city, frame_id_raw]):
        await callback.message.answer(text=Texts.Messages.missing_fields)
        await ctx.clear()
        return

    # Преобразуем frame_id в int (Redis хранит как строку)
    try:
        frame_id = int(frame_id_raw)
    except (ValueError, TypeError):
        logger.error(f"Некорректный frame_id: {frame_id_raw}")
        await callback.message.answer(text=Texts.Messages.something_went_wrong)
        await ctx.clear()
        return

    # Проверяем таймаут между сообщениями
    if Config.MESSAGES_TIME_OUT_MINUTES > 0:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.max_id == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                last_message_result = await session.execute(
                    select(Message)
                    .where(Message.user_id == user.id)
                    .order_by(Message.created_at.desc())
                    .limit(1)
                )
                last_message = last_message_result.scalar_one_or_none()
                if last_message:
                    time_diff = datetime.now() - last_message.created_at
                    if time_diff < timedelta(minutes=Config.MESSAGES_TIME_OUT_MINUTES):
                        await callback.message.answer(text=Texts.Messages.messages_time_out)
                        await ctx.clear()
                        return

    # Создаем сообщение в БД
    try:
        async with async_session() as session:
            # Получаем пользователя
            result = await session.execute(
                select(User).where(User.max_id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                logger.error(f"Пользователь {user_id} не найден в БД")
                await callback.message.answer(text=Texts.Messages.something_went_wrong)
                await ctx.clear()
                return

            # Создаем сообщение со статусом AUTO_MODERATION
            message = Message(
                user_id=user.id,
                text=message_text,
                name=name,
                city=city,
                frame_id=frame_id,
                status=MessageStatus.AUTO_MODERATION,
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            message_id = message.id

        # Отправляем на автомодерацию в фоне (не блокируем ответ пользователю)
        asyncio.create_task(auto_moderate_message(message_id))

        # Уведомляем пользователя с кнопкой для отправки еще одного сообщения
        keyboard = InlineKeyboardBuilder()
        keyboard.add(CallbackButton(text=Texts.Buttons.send_one_more_message, payload="send_message"))

        await callback.message.answer(
            text=Texts.Messages.start_moderation,
            attachments=[keyboard.as_markup()],
        )
        await ctx.clear()

    except Exception as e:
        logger.error(f"Ошибка при создании сообщения: {e}")
        await callback.message.answer(text=Texts.Messages.something_went_wrong)
        await ctx.clear()
