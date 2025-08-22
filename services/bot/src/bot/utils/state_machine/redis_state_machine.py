from .base import BaseStateMachine
from .user_state import UserState
from redis.asyncio import Redis
from ..config import Config


class RedisStateMachine(BaseStateMachine):
    def __init__(self):
        self.redis = Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_STORAGE_DB,
        )

    async def update_context(self, user_id: int, **data) -> None:
        for key, value in data.items():
            await self.redis.set(f"{user_id}:{key}", value)

    async def get_context(self, user_id: int, key: str) -> str | None:
        value = await self.redis.get(f"{user_id}:{key}")
        if value is not None:
            return value.decode("utf-8")
        return None

    async def clear_context(self, user_id: int) -> None:
        keys = await self.redis.keys(f"{user_id}:*")
        if keys:
            await self.redis.delete(*keys)

    async def set_state(self, user_id: int, state: UserState) -> None:
        await self.redis.set(str(user_id), state.value)

    async def get_state(self, user_id: int) -> UserState | None:
        state_value = await self.redis.get(str(user_id))
        if state_value is not None:
            return UserState(state_value.decode("utf-8"))
        return None

    async def clear_state(self, user_id: int) -> None:
        await self.redis.delete(str(user_id))

    async def clear(self) -> None:
        keys = await self.redis.keys("*")
        if keys:
            await self.redis.delete(*keys)
