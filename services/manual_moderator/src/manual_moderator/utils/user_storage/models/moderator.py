from .base_user import BaseUser
from typing import Annotated
from pydantic import Field
from ..user_storage import UserStorage
from shared_models.messaging import Message, ModerationResult
from shared_models.enums import ModeratorType
from shared_models.enums import ModerationResult as ModerationResultEnum
from manual_moderator.utils.config import Config
from .bot_data import BotData
from shared_models.messaging.queues.bot import bot_moderate_response_queue
from shared_models.messaging.exchanges import bot_exchange
from datetime import datetime


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

    async def __process_message(self, result: ModerationResultEnum) -> None:
        if not self.processing_message:
            raise ValueError(
                "No message is currently being processed by the moderator."
            )
        await UserStorage.broker.publish(
            ModerationResult(
                message=self.processing_message,
                source=ModeratorType.MANUAL,
                result=result,
            ),
            bot_moderate_response_queue,
            bot_exchange,
        )
        await self.add_processed_message(self.processing_message)
        self.processing_message = None
        self.last_activity = int(datetime.now(tz=Config.TIME_ZONE).timestamp())
        await self.save()

    async def approve_message(self) -> None:
        await self.__process_message(ModerationResultEnum.APPROVED)

    async def reject_message(self) -> None:
        await self.__process_message(ModerationResultEnum.REJECTED)

    async def mark_inactive(self) -> None:
        self.is_active = False
        if self.processing_message:
            await BotData.add_message_to_processing_queue(self.processing_message)
        self.processing_message = None
        await self.save()
