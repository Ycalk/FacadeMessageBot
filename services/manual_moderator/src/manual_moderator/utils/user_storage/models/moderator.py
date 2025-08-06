from .base_user import BaseUser
from typing import Annotated
from pydantic import Field
from ..user_storage import UserStorage


class Moderator(BaseUser):
    is_active: Annotated[
        bool, Field(description="Is the moderator currently working")
    ] = False

    async def get_messages_processed(self) -> int:
        return (
            await UserStorage.redis.get(f"messages_processed:{self.telegram_id}") or 0
        )

    async def set_messages_processed(self, value: int) -> None:
        await UserStorage.redis.set(f"messages_processed:{self.telegram_id}", value)
