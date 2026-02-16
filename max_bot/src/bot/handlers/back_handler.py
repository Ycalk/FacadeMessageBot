"""Универсальный обработчик кнопки 'Назад' для навигации между шагами."""

from maxapi.types import MessageCallback, CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from core.logger import get_logger

from bot.instance import get_context
from bot.states import UserStates
from bot.texts import Texts
from services.backgrounds import get_available_backgrounds

logger = get_logger(__name__)


async def back_button(callback: MessageCallback) -> None:
    """
    Универсальная кнопка 'Назад' - возвращает на предыдущий шаг
    в зависимости от текущего состояния пользователя.
    """
    user_id = callback.callback.user.user_id
    ctx = get_context(user_id)
    current_state = await ctx.get_state()

    if not current_state:
        # Если нет состояния - возвращаем к началу
        await ctx.clear()
        keyboard = InlineKeyboardBuilder()
        keyboard.add(CallbackButton(text=Texts.Buttons.send_message, payload="send_message"))
        await callback.message.answer(
            text=Texts.Messages.start,
            attachments=[keyboard.as_markup()],
        )
        return

    # В зависимости от текущего состояния возвращаемся на предыдущий шаг
    if current_state == str(UserStates.get_message):
        # С ввода текста → к началу
        await ctx.clear()
        keyboard = InlineKeyboardBuilder()
        keyboard.add(CallbackButton(text=Texts.Buttons.send_message, payload="send_message"))
        await callback.message.answer(
            text=Texts.Messages.start,
            attachments=[keyboard.as_markup()],
        )

    elif current_state == str(UserStates.get_name):
        # С имени → к вводу текста
        await callback.message.answer(text=Texts.Messages.get_message)
        await ctx.set_state(UserStates.get_message)

    elif current_state == str(UserStates.get_city):
        # С города → к имени (с предложением имени из профиля)
        first_name = getattr(callback.callback.user, "first_name", None)
        keyboard = InlineKeyboardBuilder()

        if first_name:
            keyboard.add(CallbackButton(text=first_name, payload="use_profile_name"))
            keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
            await callback.message.answer(
                text=Texts.Messages.get_name_with_name_from_profile,
                attachments=[keyboard.as_markup()],
            )
        else:
            keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
            await callback.message.answer(
                text=Texts.Messages.get_name,
                attachments=[keyboard.as_markup()],
            )

        await ctx.set_state(UserStates.get_name)

    elif current_state == str(UserStates.confirm_city):
        # С подтверждения города → к вводу города
        keyboard = InlineKeyboardBuilder()
        keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
        await callback.message.answer(
            text=Texts.Messages.add_city,
            attachments=[keyboard.as_markup()],
        )
        await ctx.set_state(UserStates.get_city)

    elif current_state == str(UserStates.choose_background):
        # С выбора фона → к подтверждению города
        data = await ctx.get_data()
        city = data.get("city", "")
        keyboard = InlineKeyboardBuilder()
        keyboard.add(CallbackButton(text="Подтвердить", payload="confirm_city"))
        keyboard.add(CallbackButton(text=Texts.Buttons.back, payload="back"))
        await callback.message.answer(
            text=Texts.Messages.confirm_city.format(city=city),
            attachments=[keyboard.as_markup()],
        )
        await ctx.set_state(UserStates.confirm_city)

    elif current_state == str(UserStates.preview):
        # С предпросмотра → к выбору фона
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

    else:
        # Неизвестное состояние
        logger.warning(f"Неизвестное состояние {current_state} для пользователя {user_id}")
        await callback.message.answer(text=Texts.Messages.wrong_step)
