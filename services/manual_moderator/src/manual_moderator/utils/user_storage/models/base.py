from pydantic import BaseModel, Field
from abc import ABC
from ..user_storage import UserStorage
from typing import Annotated, Self


class UserStorageBaseModel(BaseModel, ABC):
    telegram_id: Annotated[int, Field(description="Telegram user ID")]

    @classmethod
    async def get(cls, telegram_id: int) -> Self:
        data = await UserStorage.redis.get(f"{cls.__name__.lower()}:{telegram_id}")
        if not data:
            raise ValueError(f"{cls.__name__} with telegram_id {telegram_id} not found")

        return cls.model_validate_json(data)

    @classmethod
    async def get_or_none(cls, telegram_id: int) -> Self | None:
        try:
            return await cls.get(telegram_id)
        except ValueError:
            return None

    @classmethod
    async def all(cls) -> list[Self]:
        keys = await UserStorage.redis.keys(f"{cls.__name__.lower()}:*")
        if not keys:
            return []

        data_list = await UserStorage.redis.mget(keys)
        return [cls.model_validate_json(data) for data in data_list if data]

    @classmethod
    async def exists(cls, telegram_id: int) -> bool:
        return await UserStorage.redis.exists(f"{cls.__name__.lower()}:{telegram_id}")

    @classmethod
    async def create(cls, telegram_id: int, exist_ok: bool = True, **kwargs) -> Self:
        if await cls.exists(telegram_id):
            raise ValueError(
                f"{cls.__name__} with telegram_id {telegram_id} already exists"
            )

        instance = cls(telegram_id=telegram_id, **kwargs)
        await instance.save()
        return instance

    async def save(self) -> None:
        data = self.model_dump_json()
        await UserStorage.redis.set(
            f"{self.__class__.__name__.lower()}:{self.telegram_id}", data
        )

    async def delete(self) -> None:
        await UserStorage.redis.delete(
            f"{self.__class__.__name__.lower()}:{self.telegram_id}"
        )
