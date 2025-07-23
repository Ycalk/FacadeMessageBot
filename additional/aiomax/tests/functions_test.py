import pytest
from aiomax import Bot
from aiomax.types import BotInfo
from aiomax.types import ChatList
from aiomax.methods import GetChatList


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
