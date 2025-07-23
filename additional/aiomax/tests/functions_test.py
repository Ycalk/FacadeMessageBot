import pytest
from aiomax import Bot
from aiomax.types import BotInfo
from aiomax.types import ChatList, UpdateList
from aiomax.methods import GetChatList, GetUpdates


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
