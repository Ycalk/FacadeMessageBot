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

    @classmethod
    async def enable_auto_approve(cls) -> None:
        await UserStorage.redis.set(f"{cls.__name__.lower()}:auto_approve", "1")

    @classmethod
    async def disable_auto_approve(cls) -> None:
        await UserStorage.redis.set(f"{cls.__name__.lower()}:auto_approve", "0")

    @classmethod
    async def is_auto_approve_enabled(cls) -> bool:
        auto_approve = await UserStorage.redis.get(
            f"{cls.__name__.lower()}:auto_approve"
        )  # type: ignore
        return auto_approve == b"1" if auto_approve else False
