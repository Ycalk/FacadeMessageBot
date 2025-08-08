from redis.asyncio.client import Redis
from faststream.rabbit import RabbitBroker


class UserStorage:
    @classmethod
    async def init(
        cls, redis_host: str, redis_port: int, redis_db: int, broker: RabbitBroker
    ) -> None:
        cls.redis = Redis(host=redis_host, port=redis_port, db=redis_db)
        cls.broker = broker
        await cls.redis.ping()

    @classmethod
    async def close(cls) -> None:
        await cls.redis.close()
