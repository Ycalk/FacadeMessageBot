from .base_user import BaseUser
from typing import Annotated
from pydantic import Field
from ..user_storage import UserStorage
from shared_models.messaging import Message


class Moderator(BaseUser):
    is_active: Annotated[
        bool, Field(description="Is the moderator currently working")
    ] = False
    last_activity: Annotated[
        int | None, Field(description="Timestamp of the last activity of the moderator")
    ] = None
    processing_message: Annotated[
        Message | None,
        Field(
            description="Message currently being processed by the moderator",
            exclude=True,
        ),
    ] = None

    async def add_processed_message(self, message: Message) -> None:
        await UserStorage.redis.rpush(
            f"moderator_processed:{self.telegram_id}", message.model_dump_json()
        )  # type: ignore

    async def get_processed_messages_count(self) -> int:
        return await UserStorage.redis.llen(f"moderator_processed:{self.telegram_id}")  # type: ignore

    async def get_all_processed_messages(self) -> list[Message]:
        messages = await UserStorage.redis.lrange(
            f"moderator_processed:{self.telegram_id}", 0, -1
        )  # type: ignore
        return (
            [Message.model_validate_json(msg) for msg in messages] if messages else []
        )
