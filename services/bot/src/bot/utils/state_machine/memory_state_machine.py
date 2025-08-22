from .base import BaseStateMachine
from .user_state import UserState


class MemoryStateMachine(BaseStateMachine):
    def __init__(self):
        self._states: dict[int, UserState | None] = {}
        self._context: dict[int, dict[str, str]] = {}

    async def update_context(self, user_id: int, **data) -> None:
        if user_id not in self._context:
            self._context[user_id] = {}
        self._context[user_id].update(data)

    async def get_context(self, user_id: int, key: str) -> str | None:
        return self._context.get(user_id, {}).get(key)

    async def clear_context(self, user_id: int) -> None:
        if user_id in self._context:
            self._context[user_id] = {}

    async def set_state(self, user_id: int, state: UserState) -> None:
        self._states[user_id] = state

    async def get_state(self, user_id: int) -> UserState | None:
        return self._states.get(user_id)

    async def clear_state(self, user_id: int) -> None:
        if user_id in self._states:
            self._states[user_id] = None

    async def clear(self) -> None:
        self._states.clear()
        self._context.clear()

    def __str__(self) -> str:
        result = ["Current User States:"]
        for user_id, state in self._states.items():
            result.append((f"User ID: {user_id}, State: {state}"))
        return "\n".join(result)
