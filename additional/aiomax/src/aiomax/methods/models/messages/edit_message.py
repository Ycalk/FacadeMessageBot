from ...base import MaxMethod, QueryParameterMarker, BodyParameterMarker
from ....types import Result, AttachmentRequest, NewMessageLink, TextFormat
from pydantic import Field
from typing import Annotated


class EditMessage(MaxMethod[Result]):
    """Edit an existing message.

    Args:
        message_id (str): The ID of the message to be edited. This is a required field.
        text (str | None): New text of the message. If not provided, the text will not be changed.
        attachments (list[AttachmentRequest] | None): List of attachments. If empty, all attachments will be removed.
        link (NewMessageLink | None): Message link. If not provided, the link will not be changed.
        notify (bool): If True, the user will be notified. If False, the user will not be notified. Default is True.
        format (TextFormat | None): Text format for the message. If not provided, the default format will be used.
    """

    message_id: Annotated[
        str,
        QueryParameterMarker(),
        Field(
            ...,
            description="The ID of the message to be edited. This is a required field.",
        ),
    ]

    text: Annotated[
        str | None,
        BodyParameterMarker(),
        Field(
            ...,
            description="New text of the message.",
        ),
    ] = None

    attachments: Annotated[
        list[AttachmentRequest] | None,
        BodyParameterMarker(),
        Field(
            ...,
            description="List of attachments, if empty all attachments will be removed.",
        ),
    ] = None

    link: Annotated[
        NewMessageLink | None,
        BodyParameterMarker(),
        Field(
            None,
            description="Message link.",
        ),
    ] = None

    notify: Annotated[
        bool,
        BodyParameterMarker(),
        Field(
            ...,
            description="If True, the user will be notified. If False, the user will not be notified.",
        ),
    ] = True

    text_format: Annotated[
        TextFormat | None,
        BodyParameterMarker(),
        Field(
            None,
            description="Text format for the message. If not provided, the default format will be used.",
        ),
    ] = None

    @property
    def endpoint(self) -> str:
        return "/messages"

    @property
    def method(self) -> str:
        return "PUT"

    def load_response(self, json_data: str | bytes | bytearray) -> Result:
        return Result.model_validate_json(json_data)
