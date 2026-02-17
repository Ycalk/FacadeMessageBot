from maxapi import Router, F
from core.logger import get_logger

from bot.instance import get_context, antispam
from bot.states import UserStates
from bot.texts import Texts
from bot.handlers.get_message import get_message
from bot.handlers.get_name import get_name
from bot.handlers.get_city import get_city
from bot.handlers.wrong_step import reply_wrong_step_for_message

logger = get_logger(__name__)

text_router = Router(router_id='text')


@text_router.message_created(
    F.message.body.text & ~F.message.body.text.in_(['/start', '/me'])
)
async def _handle_text(event):
    if not event.message or not event.message.sender:
        return
    user_id = event.message.sender.user_id

    # Антиспам-проверка
    if not await antispam.record_action(user_id):
        await event.message.answer(text=Texts.Messages.spam_blocked)
        return

    ctx = get_context(user_id)
    current_state = await ctx.get_state()

    if current_state == str(UserStates.get_message):
        await get_message(event, event.bot)
    elif current_state == str(UserStates.get_name):
        await get_name(event, event.bot)
    elif current_state == str(UserStates.get_city):
        await get_city(event, event.bot)
    else:
        await reply_wrong_step_for_message(event)
        logger.debug(
            f'Неожиданное состояние {current_state} для пользователя {user_id}, отправлена подсказка'
        )
