"""Обработчик предпросмотра и отправки на модерацию."""

import asyncio
from datetime import datetime, timedelta
from functools import partial

from maxapi.types import MessageCallback, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from core.logger import get_logger

from bot.instance import get_context
from bot.states import UserStates
from bot.texts import Texts
from bot.handlers.wrong_step import reply_wrong_step_for_callback
from core.config import Config
from db.models import Message, User, MessageStatus
from db.session import async_session
from services.auto_moderator import apply_auto_approvals
from services.backgrounds import build_preview_url, generate_text_preview
from services.message_limits import can_send_more_messages

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

    # Проверяем таймаут между сообщениями (пропускаем для пользователей без лимитов)
    if Config.MESSAGES_TIME_OUT_MINUTES > 0 and user_id not in Config.unlimited_users_list:
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
                        return

    # Генерируем и сохраняем превью на диск только при отправке на модерацию
    loop = asyncio.get_event_loop()
    preview_path = await loop.run_in_executor(
        None,
        partial(generate_text_preview, frame_id, message_text, name, city),
    )
    preview_url: str | None = None
    if preview_path is not None:
        preview_url = build_preview_url(preview_path.name)
        logger.info(f"Превью сохранено для модерации: {preview_url}")
    else:
        logger.warning(f"Не удалось сгенерировать превью при отправке на модерацию (frame_id={frame_id})")

    # Создаем сообщение в БД
    # message_id инициализируем заранее, чтобы в except знать: уже в БД или нет
    message_id: int | None = None
    can_send_one_more = False
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.max_id == user_id)
            )
            user = result.scalar_one_or_none()
            if not user:
                logger.error(f"Пользователь {user_id} не найден в БД")
                await callback.message.answer(text=Texts.Messages.something_went_wrong)
                await ctx.clear()
                return

            can_send_one_more = await can_send_more_messages(user_id, additional_messages=1)

            # Создаем сообщение сразу на внутренней модерации
            message = Message(
                user_id=user.id,
                text=message_text,
                name=name,
                city=city,
                frame_id=frame_id,
                preview_url=preview_url,
                status=MessageStatus.INTERNAL_MODERATION,
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            message_id = message.id  # с этого момента сообщение уже в БД

        # Применяем автоодобрения от настроенных модераторов в фоне
        async def _run_auto_approvals() -> None:
            try:
                await apply_auto_approvals(message_id)
            except Exception as exc:
                logger.error(f"Ошибка автоодобрения для сообщения {message_id}: {exc}")

        asyncio.create_task(_run_auto_approvals())

        # Уведомляем пользователя: кнопку добавляем только если можно отправить ещё
        if can_send_one_more:
            keyboard = InlineKeyboardBuilder()
            keyboard.add(CallbackButton(text=Texts.Buttons.send_one_more_message, payload="send_message"))
            await callback.message.answer(
                text=Texts.Messages.start_moderation,
                attachments=[keyboard.as_markup()],
            )
        else:
            await callback.message.answer(text=Texts.Messages.start_moderation)
        await ctx.clear()

    except Exception as e:
        logger.error(f"Ошибка при создании/отправке уведомления: {e}")
        if message_id is not None:
            # Сообщение уже сохранено в БД — сообщаем правильно, не пугаем пользователя
            logger.warning(f"Сообщение {message_id} уже в модерации, уведомление не доставлено")
            try:
                await callback.message.answer(text=Texts.Messages.start_moderation)
            except Exception:
                pass
        else:
            # Сообщение не создано — сообщаем об ошибке
            try:
                await callback.message.answer(text=Texts.Messages.something_went_wrong)
            except Exception:
                pass
        await ctx.clear()
