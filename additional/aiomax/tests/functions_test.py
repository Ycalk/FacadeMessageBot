import pytest
import io
import asyncio
from aiomax import Bot
from aiomax.types import (
    ChatList,
    UpdateList,
    BotInfo,
    InputFile,
    BotStartedUpdate,
    User,
)
from aiomax.client import TestSession
from aiomax.types.enums import UploadType
from aiomax.methods import GetChatList, GetUpdates, GetMe
from PIL import Image


@pytest.mark.asyncio
async def test_bot_me(bot: Bot):
    """Test the bot's me method."""
    response = await bot.me()
    assert response is not None
    assert isinstance(response, BotInfo)


@pytest.mark.asyncio
async def test_bot_chats_list(bot: Bot):
    response = await bot(GetChatList())
    assert response is not None
    assert isinstance(response, ChatList)
    assert isinstance(response.chats, list)


@pytest.mark.asyncio
async def test_get_updates(bot: Bot):
    response = await bot(GetUpdates(timeout=5))
    assert response is not None
    assert isinstance(response, UpdateList)
    assert isinstance(response.updates, list)


@pytest.mark.asyncio
async def test_upload_image_file(bot: Bot):
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    file = InputFile(data=buf.read(), filename="test.jpg", upload_type=UploadType.IMAGE)
    token = await bot.upload(file)
    assert token is not None
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_register_handler_with_filter(bot: Bot):
    async def handler(update: BotStartedUpdate) -> None:
        pass

    def filter_func(update: BotStartedUpdate) -> bool:
        return True

    bot.register_handler(handler, filter_func)

    # Check if the handler is registered
    assert "bot_started" in bot._handlers
    assert bot._handlers["bot_started"][0].handler == handler
    assert bot._handlers["bot_started"][0].filter == filter_func


@pytest.mark.asyncio
async def test_register_handler_without_filter(bot: Bot):
    async def handler(update: BotStartedUpdate) -> None:
        pass

    bot.register_handler(handler)

    assert "bot_started" in bot._handlers
    assert bot._handlers["bot_started"][0].handler == handler


# Test session
@pytest.mark.asyncio
async def test_bot_get_me_in_test_session(bot_with_test_session: Bot):
    """Test the bot's get_me method in a test session."""
    response = await bot_with_test_session.me()
    assert response is not None
    assert isinstance(response, BotInfo)
    assert response.user_id == 0


@pytest.mark.asyncio
async def test_bot_update_reaction_in_test_session(
    bot_with_test_session: Bot, test_session: TestSession
):
    update = BotStartedUpdate(
        timestamp=1,
        chat_id=0,
        user=User(
            user_id=1,
            first_name="Test User",
            last_name=None,
            username=None,
            is_bot=False,
            last_activity_time=1,
        ),
        payload=None,
        user_locale="locale",
    )

    event = asyncio.Event()

    async def handler(update: BotStartedUpdate) -> None:
        await bot_with_test_session.me()
        event.set()

    bot_with_test_session.register_handler(handler)
    await test_session.add_update(update)

    await asyncio.wait_for(event.wait(), timeout=2)
    assert len(test_session.requests) == 1
    assert isinstance(test_session.requests[0], GetMe)
