from ...base import MaxMethod, QueryParameterMarker
from ....types import Result
from pydantic import Field
from typing import Annotated


class DeleteMessage(MaxMethod[Result]):
    """Delete an existing message.

    Args:
        message_id (str): The ID of the message to be deleted. This is a required field.
    """

    message_id: Annotated[
        str,
        QueryParameterMarker(),
        Field(
            ...,
            description="The ID of the message to be deleted. This is a required field.",
        ),
    ]

    @property
    def endpoint(self) -> str:
        return "/messages"

    @property
    def method(self) -> str:
        return "DELETE"

    def load_response(self, json_data: str | bytes | bytearray) -> Result:
        return Result.model_validate_json(json_data)
