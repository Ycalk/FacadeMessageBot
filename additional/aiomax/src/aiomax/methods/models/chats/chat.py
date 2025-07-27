from ...base import MaxMethod
from ....types import Chat
from pydantic import Field


class GetChat(MaxMethod[Chat]):
    """Get information about a chat.

    Args:
        chat_id (int): Unique identifier for the target chat.
    """

    chat_id: int = Field(
        ...,
        description="Unique identifier for the target chat or username of the target channel",
    )

    @property
    def endpoint(self) -> str:
        return f"/chats/{self.chat_id}"

    @property
    def method(self) -> str:
        return "GET"

    def load_response(self, json_data: str | bytes | bytearray) -> Chat:
        return Chat.model_validate_json(json_data)
