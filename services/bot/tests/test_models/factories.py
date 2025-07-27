from aiomax.types import User, Recipient, Attachment, Message, MessageBody, Callback
from uuid import uuid4


def message_factory(
    sender: User,
    recipient: Recipient,
    text: str = "Test message",
    attachments: list[Attachment] | None = None,
) -> Message:
    return Message(
        sender=sender,
        recipient=recipient,
        timestamp=1,
        link=None,
        body=MessageBody(
            mid=uuid4().hex, seq=1, text=text, attachments=attachments, markup=None
        ),
        stat=None,
        url=None,
    )


def callback_factory(payload: str, user: User) -> Callback:
    return Callback(
        timestamp=1,
        callback_id=uuid4().hex,
        payload=payload,
        user=user,
    )
