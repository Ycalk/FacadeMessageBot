from enum import StrEnum


class UserState(StrEnum):
    CONFIRM_START = "confirm_start"
    GET_MESSAGE = "get_message"
    ADD_NAME_SOLUTION = "add_name_solution"


class StateMachine:
    def __init__(self):
        self._states: dict[int, UserState] = {}

    def set_state(self, user_id: int, state: UserState):
        self._states[user_id] = state

    def get_state(self, user_id: int) -> UserState | None:
        return self._states.get(user_id)

    def __str__(self) -> str:
        result = ["Current User States:"]
        for user_id, state in self._states.items():
            result.append((f"User ID: {user_id}, State: {state}"))
        return "\n".join(result)
