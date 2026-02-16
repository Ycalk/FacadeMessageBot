from maxapi.types import MessageCallback, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from core.logger import get_logger

from bot.instance import get_context
from bot.states import UserStates
from bot.texts import Texts
from bot.handlers.wrong_step import reply_wrong_step_for_callback
from services.backgrounds import get_available_backgrounds

logger = get_logger(__name__)


async def confirm_city(callback: MessageCallback) -> None:
    user_id = callback.callback.user.user_id
    payload = callback.callback.payload
    ctx = get_context(user_id)
    current_state = await ctx.get_state()

    if current_state != str(UserStates.confirm_city):
        await reply_wrong_step_for_callback(callback)
        return

    if payload != 'confirm_city':
        return

    # Переходим к выбору фона
    backgrounds = await get_available_backgrounds()

    keyboard = InlineKeyboardBuilder()
    # Добавляем фоны по 3 кнопки в ряд
    for i in range(0, len(backgrounds) - 1, 3):
        row_buttons = []
        for j in range(3):
            if i + j < len(backgrounds):
                bg = backgrounds[i + j]
                row_buttons.append(
                    CallbackButton(text=str(bg.id), payload=f'background_{bg.id}')
                )
        keyboard.row(*row_buttons)

    # Последний фон и кнопка назад в отдельном ряду
    last_bg = backgrounds[-1]
    keyboard.row(
        CallbackButton(text=str(last_bg.id), payload=f'background_{last_bg.id}'),
        CallbackButton(text=Texts.Buttons.back, payload="back")
    )

    await callback.message.answer(
        text='🎨 Выберите фон для вашего послания:',
        attachments=[keyboard.as_markup()],
    )

    await ctx.set_state(UserStates.choose_background)
