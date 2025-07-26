from enum import StrEnum


class UserState(StrEnum):
    CONFIRM_START = "confirm_start"
    GET_MESSAGE = "get_message"
    ADD_NAME_SOLUTION = "add_name_solution"
    GET_NAME = "get_name"
    ADD_CITY_SOLUTION = "add_city_solution"
    GET_CITY = "get_city"
    CONFIRM_CITY = "confirm_city"
    GET_PHOTO_SOLUTION = "get_photo_solution"


class StateMachine:
    def __init__(self):
        self._states: dict[int, UserState] = {}
        self._context: dict[int, dict[str, str]] = {}

    def update_context(self, user_id: int, **data) -> None:
        if user_id not in self._context:
            self._context[user_id] = {}
        self._context[user_id].update(data)

    def get_context(self, user_id: int, key: str) -> str | None:
        return self._context.get(user_id, {}).get(key)

    def set_state(self, user_id: int, state: UserState) -> None:
        self._states[user_id] = state

    def get_state(self, user_id: int) -> UserState | None:
        return self._states.get(user_id)

    def __str__(self) -> str:
        result = ["Current User States:"]
        for user_id, state in self._states.items():
            result.append((f"User ID: {user_id}, State: {state}"))
        return "\n".join(result)
