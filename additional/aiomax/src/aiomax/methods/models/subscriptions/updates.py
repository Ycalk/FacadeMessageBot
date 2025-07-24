from ...base import MaxMethod, QueryParameterMarker
from ....types import UpdateList
from pydantic import Field
from typing import Annotated


class GetUpdates(MaxMethod[UpdateList]):
    """Get a list of updates.

    Args:
        limit (int): Maximum number of updates to return. Default is 100, minimum is 1, maximum is 1000.
        timeout (int): Timeout in seconds for the request. Default is 30, minimum is 0, maximum is 90.
    """

    limit: Annotated[
        int, QueryParameterMarker(), Field(ge=1, le=1000, description="Maximum updates")
    ] = 100
    timeout: Annotated[
        int,
        QueryParameterMarker(),
        Field(ge=0, le=90, description="Timeout in seconds"),
    ] = 30

    @property
    def endpoint(self) -> str:
        return "/updates"

    @property
    def method(self) -> str:
        return "GET"

    def load_response(self, json_data: str | bytes | bytearray) -> UpdateList:
        return UpdateList.model_validate_json(json_data)
