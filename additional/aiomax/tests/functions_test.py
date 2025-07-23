import pytest
import io
from aiomax import Bot
from aiomax.types import ChatList, UpdateList, BotInfo, InputFile
from aiomax.types.enums import UploadType
from aiomax.methods import GetChatList, GetUpdates
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
