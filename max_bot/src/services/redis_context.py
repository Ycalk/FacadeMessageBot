from __future__ import annotations

from typing import Any

from redis.asyncio import Redis

from maxapi.context import State


class RedisContext:
    """Drop-in замена MemoryContext с персистентным хранением в Redis Hash."""

    def __init__(
        self, redis: Redis, chat_id: int | None, user_id: int | None, ttl: int = 3600
    ):
        self.redis = redis
        self.chat_id = chat_id
        self.user_id = user_id
        self.ttl = ttl
        self._key = f"ctx:{user_id}"

    async def get_state(self) -> str | None:
        value = await self.redis.hget(self._key, "__state__")
        if value is not None:
            return value.decode("utf-8") if isinstance(value, bytes) else value
        return None

    async def set_state(self, state: State | str | None = None) -> None:
        if state is None:
            await self.redis.hdel(self._key, "__state__")
        else:
            await self.redis.hset(self._key, "__state__", str(state))
            await self.redis.expire(self._key, self.ttl)

    async def get_data(self) -> dict[str, Any]:
        raw = await self.redis.hgetall(self._key)
        result: dict[str, Any] = {}
        for k, v in raw.items():
            key = k.decode("utf-8") if isinstance(k, bytes) else k
            if key == "__state__":
                continue
            result[key] = v.decode("utf-8") if isinstance(v, bytes) else v
        return result

    async def update_data(self, **kwargs: Any) -> None:
        if kwargs:
            mapping = {k: str(v) for k, v in kwargs.items()}
            await self.redis.hset(self._key, mapping=mapping)
            await self.redis.expire(self._key, self.ttl)

    async def set_data(self, data: dict[str, Any]) -> None:
        state = await self.get_state()
        await self.redis.delete(self._key)
        mapping: dict[str, str] = {}
        if state:
            mapping["__state__"] = state
        for k, v in data.items():
            mapping[k] = str(v)
        if mapping:
            await self.redis.hset(self._key, mapping=mapping)
            await self.redis.expire(self._key, self.ttl)

    async def clear(self) -> None:
        await self.redis.delete(self._key)
