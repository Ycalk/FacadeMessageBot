from ..user_storage import UserStorage
from shared_models.messaging import Message


class BotData:
    @classmethod
    async def get_processing_queue_length(cls) -> int:
        return await UserStorage.redis.llen(f"{cls.__name__.lower()}:processing_queue")  # type: ignore

    @classmethod
    async def add_message_to_processing_queue(cls, message: Message) -> None:
        await UserStorage.redis.rpush(
            f"{cls.__name__.lower()}:processing_queue", message.model_dump_json()
        )  # type: ignore

    @classmethod
    async def get_new_processing_message(cls) -> Message | None:
        message_json = await UserStorage.redis.lpop(
            f"{cls.__name__.lower()}:processing_queue"
        )  # type: ignore
        if message_json:
            return Message.model_validate_json(message_json)  # type: ignore
        return None
