from redis.asyncio import Redis
from .base import BaseStorage
from uuid import UUID
from .models import Image, ShownMessage
from datetime import datetime


class RedisStorage(BaseStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def save_image(self, image: Image) -> UUID:
        await self.redis.set(f"image:{image.id}", image.model_dump_json())
        await self.redis.zadd(
            "images_by_created_time",
            {str(image.id): image.created_at.timestamp()},
        )
        return image.id

    async def save_shown_message(self, message: ShownMessage) -> UUID:
        await self.redis.set(f"shown_message:{message.id}", message.model_dump_json())
        await self.redis.zadd(
            "shown_messages_by_show_at_time",
            {str(message.id): message.show_at.timestamp()},
        )
        return message.id

    async def find_images_by_created_time(
        self, start: datetime, end: datetime
    ) -> list[Image]:
        image_ids = await self.redis.zrangebyscore(
            "images_by_created_time",
            min=start.timestamp(),
            max=end.timestamp(),
        )
        values = await self.redis.mget([f"image:{image_id}" for image_id in image_ids])

        return [
            Image.model_validate_json(value) for value in values if value is not None
        ]

    async def find_shown_messages_by_show_at_time(
        self, start: datetime, end: datetime
    ) -> list[ShownMessage]:
        messages = await self.redis.zrangebyscore(
            "shown_messages_by_show_at_time",
            min=start.timestamp(),
            max=end.timestamp(),
        )
        values = await self.redis.mget(
            [f"shown_message:{message_id}" for message_id in messages]
        )

        return [
            ShownMessage.model_validate_json(value)
            for value in values
            if value is not None
        ]

    async def get_shown_messages(self) -> list[ShownMessage]:
        message_ids = await self.redis.zrange("shown_messages_by_show_at_time", 0, -1)
        values = await self.redis.mget(
            [f"shown_message:{message_id}" for message_id in message_ids]
        )
        return [
            ShownMessage.model_validate_json(value)
            for value in values
            if value is not None
        ]

    async def delete_image(self, image: Image | UUID) -> None:
        image_id = image.id if isinstance(image, Image) else image
        await self.redis.delete(f"image:{image_id}")
        await self.redis.zrem("images_by_created_time", str(image_id))

    async def delete_shown_message(self, message: ShownMessage | UUID) -> None:
        message_id = message.id if isinstance(message, ShownMessage) else message
        await self.redis.delete(f"shown_message:{message_id}")
        await self.redis.zrem("shown_messages_by_show_at_time", str(message_id))

    async def delete_old_images(self, to_date: datetime) -> None:
        image_ids = await self.redis.zrangebyscore(
            "images_by_created_time",
            min=0,
            max=to_date.timestamp(),
        )
        await self.redis.delete(*[f"image:{image_id}" for image_id in image_ids])
        await self.redis.zremrangebyscore(
            "images_by_created_time",
            min=0,
            max=to_date.timestamp(),
        )

    async def delete_old_shown_messages(self, to_date: datetime) -> None:
        message_ids = await self.redis.zrangebyscore(
            "shown_messages_by_show_at_time",
            min=0,
            max=to_date.timestamp(),
        )
        await self.redis.delete(
            *[f"shown_message:{message_id}" for message_id in message_ids]
        )
        await self.redis.zremrangebyscore(
            "shown_messages_by_show_at_time",
            min=0,
            max=to_date.timestamp(),
        )
