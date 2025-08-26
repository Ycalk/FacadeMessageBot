import pytest
import asyncio
from bot.handlers import send_message_handler, send_message_filter
from tests.conftest import handler_with_event
from bot.bot import state_machine
from bot.utils import UserState, Texts, Config
from aiomax.client import Bot, TestSession, TestResponse
from aiomax.types import (
    BotInfo,
    Recipient,
    UserWithPhoto,
    Result,
    LinkButton,
    CallbackButton,
)
from aiomax.methods import AnswerCallback
from aiomax.types.updates import MessageCallbackUpdate
from shared_models.database import User
from tests.test_models import callback_factory, message_factory


@pytest.mark.asyncio
async def test_send_message_handler_user_not_registered(
    test_session: TestSession,
    bot: Bot,
    bot_info: BotInfo,
    user_recipient: Recipient,
    user_with_photo: UserWithPhoto,
    result: Result,
):
    """Test the behavior of the confirm_start handler. With correct state and callback payload."""
    await state_machine.set_state(user_with_photo.user_id, UserState.SEND_MESSAGE)

    event = asyncio.Event()
    bot.register_handler(
        handler_with_event(send_message_handler, event),
        filter=send_message_filter,
    )

    test_session.responses = [
        TestResponse[Result](AnswerCallback, result),
    ]
    update_callback = callback_factory("send_message", user_with_photo)
    await test_session.add_update(
        MessageCallbackUpdate(
            timestamp=1,
            callback=update_callback,
            message=message_factory(bot_info, user_recipient),
            user_locale=None,
        )
    )

    try:
        await asyncio.wait_for(event.wait(), timeout=2)
    finally:
        assert (
            await state_machine.get_state(user_with_photo.user_id)
            == UserState.GET_MESSAGE
        )

        assert len(test_session.requests) == 1

        # Edit message with get message prompt
        assert isinstance(test_session.requests[0], AnswerCallback)
        assert test_session.requests[0].callback_id == update_callback.callback_id
        assert test_session.requests[0].message is not None
        assert test_session.requests[0].message.text == Texts.Messages.get_message
        assert test_session.requests[0].message.attachments == []

        # Ensure user is created in the database
        user = await User.get_or_none(max_id=user_with_photo.user_id)
        assert user is not None
        assert user.first_name == user_with_photo.first_name
        assert user.last_name == user_with_photo.last_name
        assert user.username == user_with_photo.username


@pytest.mark.asyncio
async def test_send_message_handler_user_registered(
    test_session: TestSession,
    bot: Bot,
    bot_info: BotInfo,
    user_recipient: Recipient,
    user_with_photo: UserWithPhoto,
    result: Result,
):
    """Test the behavior of the confirm_start handler. With correct state and callback payload."""
    await state_machine.set_state(user_with_photo.user_id, UserState.SEND_MESSAGE)
    # Simulate that the user is already registered
    await User.create(
        first_name=user_with_photo.first_name,
        last_name=user_with_photo.last_name,
        username=user_with_photo.username,
        max_id=user_with_photo.user_id,
    )

    event = asyncio.Event()
    bot.register_handler(
        handler_with_event(send_message_handler, event),
        filter=send_message_filter,
    )

    test_session.responses = [
        TestResponse[Result](AnswerCallback, result),
    ]
    update_callback = callback_factory("send_message", user_with_photo)
    await test_session.add_update(
        MessageCallbackUpdate(
            timestamp=1,
            callback=update_callback,
            message=message_factory(bot_info, user_recipient),
            user_locale=None,
        )
    )

    try:
        await asyncio.wait_for(event.wait(), timeout=2)
    finally:
        assert (
            await state_machine.get_state(user_with_photo.user_id)
            == UserState.GET_MESSAGE
        )

        assert len(test_session.requests) == 1

        # Edit message with get message prompt
        assert isinstance(test_session.requests[0], AnswerCallback)
        assert test_session.requests[0].callback_id == update_callback.callback_id
        assert test_session.requests[0].message is not None
        assert test_session.requests[0].message.text == Texts.Messages.get_message
        assert test_session.requests[0].message.attachments == []

        # Ensure user is still in the database
        user = await User.get_or_none(max_id=user_with_photo.user_id)
        assert user is not None
        assert user.first_name == user_with_photo.first_name
        assert user.last_name == user_with_photo.last_name
        assert user.username == user_with_photo.username


@pytest.mark.asyncio
async def test_send_message_handler_incorrect_callback_payload(
    test_session: TestSession,
    bot: Bot,
    bot_info: BotInfo,
    user_recipient: Recipient,
    user_with_photo: UserWithPhoto,
    result: Result,
):
    """Test the behavior of the confirm_start handler. With incorrect callback payload."""
    await state_machine.set_state(user_with_photo.user_id, UserState.SEND_MESSAGE)

    event = asyncio.Event()
    bot.register_handler(
        handler_with_event(send_message_handler, event),
        filter=send_message_filter,
    )

    update_callback = callback_factory("Some incorrect payload", user_with_photo)
    await test_session.add_update(
        MessageCallbackUpdate(
            timestamp=1,
            callback=update_callback,
            message=message_factory(bot_info, user_recipient),
            user_locale=None,
        )
    )

    with pytest.raises(asyncio.TimeoutError):
        # Wait for the event to be set, which should not happen
        # because the handler should not process the update
        await asyncio.wait_for(event.wait(), timeout=2)

    # Ensure the state remains unchanged
    assert (
        await state_machine.get_state(user_with_photo.user_id) == UserState.SEND_MESSAGE
    )

    # No requests should be made since the handler should not process the update
    assert len(test_session.requests) == 0

    # Ensure no user is added to the database
    user = await User.get_or_none(max_id=user_with_photo.user_id)
    assert user is None


@pytest.mark.asyncio
async def test_send_message_handler_incorrect_state(
    test_session: TestSession,
    bot: Bot,
    bot_info: BotInfo,
    user_recipient: Recipient,
    user_with_photo: UserWithPhoto,
    result: Result,
):
    """Test the behavior of the confirm_start handler. With incorrect state"""
    await state_machine.set_state(user_with_photo.user_id, UserState.GET_PHOTO_SOLUTION)

    event = asyncio.Event()
    bot.register_handler(
        handler_with_event(send_message_handler, event),
        filter=send_message_filter,
    )

    update_callback = callback_factory("send_message", user_with_photo)
    await test_session.add_update(
        MessageCallbackUpdate(
            timestamp=1,
            callback=update_callback,
            message=message_factory(bot_info, user_recipient),
            user_locale=None,
        )
    )

    with pytest.raises(asyncio.TimeoutError):
        # Wait for the event to be set, which should not happen
        # because the handler should not process the update
        await asyncio.wait_for(event.wait(), timeout=2)

    # Ensure the state remains unchanged
    assert (
        await state_machine.get_state(user_with_photo.user_id)
        == UserState.GET_PHOTO_SOLUTION
    )

    # No requests should be made since the handler should not process the update
    assert len(test_session.requests) == 0

    # Ensure no user is added to the database
    user = await User.get_or_none(max_id=user_with_photo.user_id)
    assert user is None
