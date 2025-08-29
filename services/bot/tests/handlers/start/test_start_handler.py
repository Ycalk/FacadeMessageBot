import pytest
import asyncio
from bot.handlers import start_handler
from tests.conftest import handler_with_event
from bot.bot import state_machine
from bot.utils import UserState, Texts
from maxapi.client import Bot, TestSession, TestResponse
from maxapi.types import Message, BotInfo, Recipient, UserWithPhoto, CallbackButton
from maxapi.methods import SendMessage
from maxapi.types import BotStarted
from tests.test_models import message_factory


@pytest.mark.asyncio
async def test_start_handler_behavior(
    test_session: TestSession,
    bot: Bot,
    bot_started_update: BotStarted,
    bot_info: BotInfo,
    user_recipient: Recipient,
    user_with_photo: UserWithPhoto,
):
    event = asyncio.Event()
    bot.register_handler(handler_with_event(start_handler, event))
    test_session.responses = [
        TestResponse[Message](SendMessage, message_factory(bot_info, user_recipient))
    ]
    await test_session.add_update(bot_started_update)
    try:
        await asyncio.wait_for(event.wait(), timeout=2)
    finally:
        assert (
            await state_machine.get_state(user_with_photo.user_id)
            == UserState.SEND_MESSAGE
        )

        assert len(test_session.requests) == 1

        # Send start message
        assert isinstance(test_session.requests[0], SendMessage)
        assert test_session.requests[0].text == Texts.Messages.start
        assert test_session.requests[0].user_id == user_with_photo.user_id
        assert test_session.requests[0].attachments is not None
        assert test_session.requests[0].attachments[0].type == "inline_keyboard"

        # Confirmation message contains buttons
        buttons = test_session.requests[0].attachments[0].payload.buttons
        assert len(buttons) == 2  # Два ряда кнопок
        assert len(buttons[0]) == 1  # Первый ряд: ссылка на условия
        assert len(buttons[1]) == 1  # Второй ряд: кнопка отправить сообщение

        # Проверим кнопку отправить сообщение
        send_button = buttons[1][0]
        assert isinstance(send_button, CallbackButton)
        assert send_button.text == Texts.Buttons.send_message
        assert send_button.payload == "send_message"
