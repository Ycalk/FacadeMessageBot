import pytest
from aiomax.types.updates import BotStartedUpdate
from aiomax.types import UserWithPhoto


@pytest.fixture
def bot_started_update(user_with_photo: UserWithPhoto) -> BotStartedUpdate:
    return BotStartedUpdate(
        timestamp=0, chat_id=0, user=user_with_photo, payload=None, user_locale="test"
    )
