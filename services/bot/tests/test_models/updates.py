import pytest
from maxapi.types import BotStarted
from maxapi.types import UserWithPhoto


@pytest.fixture
def bot_started_update(user_with_photo: UserWithPhoto) -> BotStarted:
    return BotStarted(
        timestamp=0, chat_id=0, user=user_with_photo, payload=None, user_locale="test"
    )
