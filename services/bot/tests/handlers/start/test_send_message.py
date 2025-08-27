import pytest
import asyncio
from datetime import datetime, timedelta
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
from shared_models.database import User, Message
from shared_models.enums import MessageState
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
async def test_send_message_handler_messages_limit_reached(
    test_session: TestSession,
    bot: Bot,
    bot_info: BotInfo,
    user_recipient: Recipient,
    user_with_photo: UserWithPhoto,
    result: Result,
):
    """Test that handler blocks user when message limit is reached."""
    await state_machine.set_state(user_with_photo.user_id, UserState.SEND_MESSAGE)
    
    # Create user and messages up to limit
    user = await User.create(
        first_name=user_with_photo.first_name,
        last_name=user_with_photo.last_name,
        username=user_with_photo.username,
        max_id=user_with_photo.user_id,
    )
    
    # Create messages up to the limit
    for i in range(Config.MAXIMUM_MESSAGES_PER_USER):
        await Message.create(
            user=user,
            text=f"Test message {i}",
            name="Test Name",
            city="Test City",
            state=MessageState.APPROVED,
            send_photo=False,
        )

    event = asyncio.Event()
    bot.register_handler(
        handler_with_event(send_message_handler, event),
        filter=send_message_filter,
    )

    test_session.responses = [TestResponse[Result](AnswerCallback, result)]
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
        # State should remain unchanged
        assert (
            await state_machine.get_state(user_with_photo.user_id)
            == UserState.SEND_MESSAGE
        )

        assert len(test_session.requests) == 1
        assert isinstance(test_session.requests[0], AnswerCallback)
        assert test_session.requests[0].message.text == Texts.Messages.messages_limit


@pytest.mark.asyncio
async def test_send_message_handler_attempts_limit_reached(
    test_session: TestSession,
    bot: Bot,
    bot_info: BotInfo,
    user_recipient: Recipient,
    user_with_photo: UserWithPhoto,
    result: Result,
):
    """Test that handler blocks user when attempts limit is reached."""
    await state_machine.set_state(user_with_photo.user_id, UserState.SEND_MESSAGE)
    
    # Create user and rejected messages up to limit
    user = await User.create(
        first_name=user_with_photo.first_name,
        last_name=user_with_photo.last_name,
        username=user_with_photo.username,
        max_id=user_with_photo.user_id,
    )
    
    # Create rejected messages up to the limit
    for i in range(Config.MAXIMUM_ATTEMPTS_PER_MESSAGE):
        await Message.create(
            user=user,
            text=f"Rejected message {i}",
            name="Test Name",
            city="Test City",
            state=MessageState.REJECTED,
            send_photo=False,
        )

    event = asyncio.Event()
    bot.register_handler(
        handler_with_event(send_message_handler, event),
        filter=send_message_filter,
    )

    test_session.responses = [TestResponse[Result](AnswerCallback, result)]
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
        # State should remain unchanged
        assert (
            await state_machine.get_state(user_with_photo.user_id)
            == UserState.SEND_MESSAGE
        )

        assert len(test_session.requests) == 1
        assert isinstance(test_session.requests[0], AnswerCallback)
        assert test_session.requests[0].message.text == Texts.Messages.attempts_limit


@pytest.mark.asyncio
async def test_send_message_handler_timeout_not_reached(
    test_session: TestSession,
    bot: Bot,
    bot_info: BotInfo,
    user_recipient: Recipient,
    user_with_photo: UserWithPhoto,
    result: Result,
):
    """Test that handler blocks user when timeout has not passed."""
    await state_machine.set_state(user_with_photo.user_id, UserState.SEND_MESSAGE)
    
    # Create user and a recent message
    user = await User.create(
        first_name=user_with_photo.first_name,
        last_name=user_with_photo.last_name,
        username=user_with_photo.username,
        max_id=user_with_photo.user_id,
    )
    
    # Create a recent message (within timeout period)
    recent_time = datetime.now() - timedelta(seconds=30)  # 30 seconds ago, less than timeout
    await Message.create(
        user=user,
        text="Recent message",
        name="Test Name", 
        city="Test City",
        state=MessageState.APPROVED,
        send_photo=False,
        created_at=recent_time,
    )

    event = asyncio.Event()
    bot.register_handler(
        handler_with_event(send_message_handler, event),
        filter=send_message_filter,
    )

    test_session.responses = [TestResponse[Result](AnswerCallback, result)]
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
        # State should remain unchanged
        assert (
            await state_machine.get_state(user_with_photo.user_id)
            == UserState.SEND_MESSAGE
        )

        assert len(test_session.requests) == 1
        assert isinstance(test_session.requests[0], AnswerCallback)
        assert test_session.requests[0].message.text == Texts.Messages.messages_time_out


@pytest.mark.asyncio
async def test_send_message_handler_message_collection_stopped(
    test_session: TestSession,
    bot: Bot,
    bot_info: BotInfo,
    user_recipient: Recipient,
    user_with_photo: UserWithPhoto,
    result: Result,
):
    """Test that handler blocks when message collection is globally stopped."""
    await state_machine.set_state(user_with_photo.user_id, UserState.SEND_MESSAGE)
    
    # Mock the config to simulate collection stopped
    original_value = Config.MESSAGE_COLLECTION_STOPPED
    Config.MESSAGE_COLLECTION_STOPPED = True
    
    try:
        event = asyncio.Event()
        bot.register_handler(
            handler_with_event(send_message_handler, event),
            filter=send_message_filter,
        )

        test_session.responses = [TestResponse[Result](AnswerCallback, result)]
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
            # State should remain unchanged
            assert (
                await state_machine.get_state(user_with_photo.user_id)
                == UserState.SEND_MESSAGE
            )

            assert len(test_session.requests) == 1
            assert isinstance(test_session.requests[0], AnswerCallback)
            assert test_session.requests[0].message.text == Texts.Messages.message_collection_stopped
            
            # User should still be created
            user = await User.get_or_none(max_id=user_with_photo.user_id)
            assert user is not None
            
    finally:
        # Restore original config value
        Config.MESSAGE_COLLECTION_STOPPED = original_value


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
