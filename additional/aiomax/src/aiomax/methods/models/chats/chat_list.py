from ...base import MaxMethod, QueryParameterMarker
from ....types import ChatList
from pydantic import Field
from typing import Annotated


class GetChatList(MaxMethod[ChatList]):
    """Get a list of chats.

    Args:
        count (int): Maximum number of chats to return. Default is 50, minimum is 1, maximum is 100.
        marker (str | None): Marker for pagination, used to get the next set of chats. Use None for the first page.
    """

    count: Annotated[
        int,
        QueryParameterMarker(),
        Field(50, ge=1, le=100, description="Maximum number of chats to return"),
    ] = 50
    marker: Annotated[
        str | None,
        QueryParameterMarker(),
        Field(
            None,
            description="Marker for pagination, used to get the next set of chats. Use None for first page",
        ),
    ] = None

    @property
    def endpoint(self) -> str:
        return "/chats"

    @property
    def method(self) -> str:
        return "GET"

    def load_response(self, json_data: str | bytes | bytearray) -> ChatList:
        return ChatList.model_validate_json(json_data)
