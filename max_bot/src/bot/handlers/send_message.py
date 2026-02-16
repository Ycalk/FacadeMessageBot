from core.logger import get_logger

from maxapi.types import MessageCallback, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from sqlalchemy import select, func

from bot.instance import get_context
from bot.states import UserStates
from bot.texts import Texts
from core.config import Config
from db.models import Message, User
from db.session import async_session

logger = get_logger(__name__)


async def _get_or_create_user(callback: MessageCallback) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.max_id == callback.callback.user.user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                max_id=callback.callback.user.user_id,
                first_name=getattr(callback.callback.user, "first_name", None),
                username=getattr(callback.callback.user, "username", None),
            )
            session.add(user)
            await session.commit()


async def _messages_limit_reached(user_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.max_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False
        count_result = await session.execute(
            select(func.count(Message.id)).where(Message.user_id == user.id)
        )
        count = count_result.scalar() or 0
        if Config.MAXIMUM_MESSAGES_PER_USER <= 0:
            return False
        return count >= Config.MAXIMUM_MESSAGES_PER_USER

async def send_message_handler(callback: MessageCallback) -> None:
    await _get_or_create_user(callback)
    user_id = callback.callback.user.user_id
    ctx = get_context(user_id)

    # Проверяем, есть ли активное состояние
    current_state = await ctx.get_state()
    if current_state:
        # Очищаем предыдущее состояние если пользователь хочет начать заново
        await ctx.clear()

    if await _messages_limit_reached(user_id):
        await callback.message.answer(text=Texts.Messages.messages_limit)
        return

    # Переходим к запросу текста поздравления (первый шаг)
    await callback.message.answer(text=Texts.Messages.get_message)
    await ctx.set_state(UserStates.get_message)
