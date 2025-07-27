from ...base import MaxMethod, QueryParameterMarker, BodyParameterMarker
from ....types import Result, NewMessageBody
from pydantic import Field
from typing import Annotated


class AnswerCallback(MaxMethod[Result]):
    """Answer a callback button press.

    Args:
        callback_id (str): The ID of the button that was pressed. This is a required field.
        message (NewMessageBody | None): New message body. If not provided, the message will not be changed.
        notification (str | None): Notification text. If not provided, the notification will not be sent.
    """

    callback_id: Annotated[
        str,
        QueryParameterMarker(),
        Field(
            ...,
            description="The ID of the button that was pressed. This is a required field.",
        ),
    ]

    message: Annotated[
        NewMessageBody | None,
        BodyParameterMarker(),
        Field(
            None,
            description="New message body. If not provided, the message will not be changed.",
        ),
    ] = None

    notification: Annotated[
        str | None,
        BodyParameterMarker(),
        Field(
            None,
            description="Notification text. If not provided, the notification will not be sent.",
        ),
    ] = None

    @property
    def endpoint(self) -> str:
        return "/answers"

    @property
    def method(self) -> str:
        return "POST"

    def load_response(self, json_data: str | bytes | bytearray) -> Result:
        return Result.model_validate_json(json_data)
