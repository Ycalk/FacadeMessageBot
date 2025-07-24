from ...base import MaxMethod, QueryParameterMarker, BodyParameterMarker
from ....types import Message, AttachmentRequest, NewMessageLink, TextFormat
from ....types.base import UNSET, UNSET_TYPE
from pydantic import Field
import json
from typing import Annotated, Sequence


class SendMessage(MaxMethod[Message]):
    """Send a message to a user or chat.

    Args:
        user_id (int | UNSET_TYPE): The ID of the user to send the message to. Use this parameter if you want to send a message to a user.
        chat_id (int | UNSET_TYPE): The ID of the chat to send the message to. Use this parameter if you want to send a message to a chat.
        disable_link_preview (bool): If False, the server will not generate a link preview for the message.
        text (str): The text of the message to be sent. This is a required field.
        attachments (list[AttachmentRequest] | None): List of attachments to be sent with the message.
        link (NewMessageLink | None): Message link.
        notify (bool): If True, the user will be notified about the message. If False, the user will not be notified.
        text_format (TextFormat | None): Text format for the message. If not provided, the default format will be used.
    """

    user_id: Annotated[
        int | UNSET_TYPE,
        QueryParameterMarker(),
        Field(
            ..., description="If you want to send message to user, use this parameter"
        ),
    ] = UNSET

    chat_id: Annotated[
        int | UNSET_TYPE,
        QueryParameterMarker(),
        Field(
            ..., description="If you want to send message to chat, use this parameter"
        ),
    ] = UNSET

    disable_link_preview: Annotated[
        bool,
        QueryParameterMarker(),
        Field(
            ...,
            description="Disable link preview for the message. If False, server will not generate link preview for the message",
        ),
    ] = True

    text: Annotated[
        str,
        BodyParameterMarker(),
        Field(
            ...,
            description="The text of the message to be sent. This is a required field.",
        ),
    ]

    attachments: Annotated[
        Sequence[AttachmentRequest] | None,
        BodyParameterMarker(),
        Field(
            ...,
            description="List of attachments to be sent with the message.",
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
            description="If True, the user will be notified about the message. If False, the user will not be notified.",
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
        return "POST"

    def load_response(self, json_data: str | bytes | bytearray) -> Message:
        result = json.loads(json_data)
        return Message.model_validate(result["message"])
