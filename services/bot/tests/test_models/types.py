import pytest
from maxapi.types import BotInfo, UserWithPhoto, Recipient, ChatType, Result


@pytest.fixture(scope="session")
def bot_info() -> BotInfo:
    return BotInfo(
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
    )


@pytest.fixture(scope="session", params=["test_user", None])
def user_with_photo(request) -> UserWithPhoto:
    return UserWithPhoto(
        user_id=1,
        first_name="TestUser",
        last_name=request.param,
        username=request.param,
        is_bot=False,
        last_activity_time=1,
        description=request.param,
        avatar_url=None,
        full_avatar_url=None,
    )


@pytest.fixture(scope="session")
def user_recipient(user_with_photo: UserWithPhoto) -> Recipient:
    return Recipient(
        user_id=user_with_photo.user_id, chat_type=ChatType.DIALOG, chat_id=None
    )


@pytest.fixture(scope="session")
def bot_recipient(bot_info: BotInfo) -> Recipient:
    return Recipient(user_id=bot_info.user_id, chat_type=ChatType.DIALOG, chat_id=None)


@pytest.fixture(scope="session")
def result() -> Result:
    return Result(success=True, message=None)
