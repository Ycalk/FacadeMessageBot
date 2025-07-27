import pytest
import logging
import asyncio
from functools import wraps
import pytest_asyncio
from aiomax import Bot
from aiomax.types import BotInfo
from aiomax.methods import GetMe
from aiomax.client import TestResponse, TestSession
from asyncio import Event
from aiomax.client.bot import UpdateT
from bot.bot import state_machine
from typing import Callable, Awaitable, AsyncGenerator

from tests.test_models.types import *  # noqa: F403
from tests.test_models.updates import *  # noqa: F403


def handler_with_event(
    handler: Callable[[UpdateT, Bot], Awaitable[None]], event: Event
) -> Callable[[UpdateT, Bot], Awaitable[None]]:
    @wraps(handler)
    async def wrapper(update: UpdateT, bot: Bot) -> None:
        await handler(update, bot)
        event.set()

    return wrapper


@pytest.fixture(scope="function")
def test_session(bot_info: BotInfo) -> TestSession:
    """Fixture to create a test session for the bot."""
    return TestSession(responses=[TestResponse[BotInfo](GetMe, bot_info)])


@pytest_asyncio.fixture(scope="function")
async def bot(test_session: TestSession) -> AsyncGenerator[Bot, None]:
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


@pytest.fixture(scope="function", autouse=True)
def clear_user_state():
    state_machine.clear()
