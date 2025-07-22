from ..base import MaxObject
from pydantic import Field
from .user import User
from .recipient import Recipient
from .linked_message import LinkedMessage
from .message_body import MessageBody
from .message_stat import MessageStat


class Message(MaxObject):
    sender: User | None = Field(None, description="User who sent the message")
    recipient: Recipient = Field(..., description="Recipient of the message")
    timestamp: int = Field(
        ...,
        description="Timestamp of when the message was created, in Unix time format",
    )
    link: LinkedMessage | None = Field(
        None,
        description="Linked message information, if the message is a link to another message",
    )
    body: MessageBody = Field(
        ...,
        description="The body of the message, containing text and optional attachments",
    )
    stat: MessageStat | None = Field(
        None,
        description="Statistics for the message, such as views",
    )
    url: str | None = Field(
        None,
        description="URL of the message, if applicable",
    )
