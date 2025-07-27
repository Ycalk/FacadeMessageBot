import pytest
import asyncio
import pytest_asyncio
from aiomax import Bot
from aiomax.client import TestSession, TestResponse
from aiomax.types import BotInfo
from aiomax.methods import GetMe
from typing import AsyncGenerator
from dotenv import load_dotenv
import os
import logging

load_dotenv()


@pytest.fixture(scope="function")
def bot() -> Bot:
    return Bot(os.getenv("TOKEN", ""), logging_level=logging.DEBUG)


@pytest.fixture(scope="session")
def test_session() -> TestSession:
    return TestSession(
        responses=[
            TestResponse(
                GetMe,
                BotInfo(
                    user_id=0,
                    first_name="TestBot",
                    last_name="Test",
                    username="test_bot",
                    is_bot=True,
                    last_activity_time=1,
                    description="This is a test bot. If you see this, it means the bot is using test session.",
                    avatar_url=None,
                    full_avatar_url=None,
                    commands=None,
                ),
            ),
        ]
    )


@pytest_asyncio.fixture(scope="function")
async def bot_with_test_session(test_session: TestSession) -> AsyncGenerator[Bot, None]:
    bot = Bot("test_token", session=test_session, logging_level=logging.DEBUG)
    polling_task = asyncio.create_task(bot.start_polling())
    try:
        yield bot
    finally:
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass
