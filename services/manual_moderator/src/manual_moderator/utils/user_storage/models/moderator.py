from .base_user import BaseUser
from typing import Annotated
from pydantic import Field
from ..user_storage import UserStorage
from shared_models.messaging import Message


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

    async def add_message(self, message: Message) -> None:
        await UserStorage.redis.rpush(
            f"moderator_queue:{self.telegram_id}", message.model_dump_json()
        )  # type: ignore

    async def get_queue_length(self) -> int:
        return await UserStorage.redis.llen(f"moderator_queue:{self.telegram_id}")  # type: ignore

    async def get_message(self) -> Message | None:
        message = await UserStorage.redis.lpop(f"moderator_queue:{self.telegram_id}")  # type: ignore
        if message:
            return Message.model_validate_json(message)  # type: ignore
        return None

    async def get_all_messages(self) -> list[Message]:
        messages = await UserStorage.redis.lrange(
            f"moderator_queue:{self.telegram_id}", 0, -1
        )  # type: ignore
        return (
            [Message.model_validate_json(msg) for msg in messages] if messages else []
        )
