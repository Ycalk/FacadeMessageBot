from redis.asyncio import Redis
from .config import Config
from shared_models.messaging import Message


class Storage:
    def __init__(self):
        self.redis = Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_STORAGE_DB,
        )

    async def add_message(self, message: Message):
        await self.redis.set(f"message:{message.message_id}", message.model_dump_json())

    async def get_message(self, message_id: int) -> Message | None:
        data = await self.redis.get(f"message:{message_id}")
        if data:
            return Message.model_validate_json(data)
        return None

    async def delete_message(self, message_id: int):
        await self.redis.delete(f"message:{message_id}")
