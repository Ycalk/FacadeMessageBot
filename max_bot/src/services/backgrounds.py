"""Сервис для работы с фонами."""

from typing import List
from pydantic import BaseModel


class Background(BaseModel):
    """Модель фона."""
    id: int
    name: str
    preview_url: str | None = None


async def get_available_backgrounds() -> List[Background]:
    """
    Получить список доступных фонов.
    Пока замокано - возвращает 10 фонов.
    """
    # TODO: В будущем получать из реального источника
    return [
        Background(id=i, name=f"Фон {i}")
        for i in range(1, 11)
    ]
