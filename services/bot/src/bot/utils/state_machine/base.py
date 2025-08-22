from abc import ABC, abstractmethod
from .user_state import UserState


class BaseStateMachine(ABC):
    @abstractmethod
    async def update_context(self, user_id: int, **data) -> None: ...

    @abstractmethod
    async def get_context(self, user_id: int, key: str) -> str | None: ...

    @abstractmethod
    async def clear_context(self, user_id: int) -> None: ...

    @abstractmethod
    async def set_state(self, user_id: int, state: UserState) -> None: ...

    @abstractmethod
    async def get_state(self, user_id: int) -> UserState | None: ...

    @abstractmethod
    async def clear_state(self, user_id: int) -> None: ...

    @abstractmethod
    async def clear(self) -> None: ...
