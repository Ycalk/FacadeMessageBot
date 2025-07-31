from pydantic import BaseModel, Field
from typing import Annotated, Optional


class Message(BaseModel):
    """

    Args:
        - message_id (int) :Unique identifier for the message.
        - text (str) :Content of the message.
        - city (str | None) :Optional city provided for the message. Defaults to None.
        - name (str | None) :Optional name provided for the message. Defaults to None.
    """

    message_id: Annotated[
        int, Field(..., description="Unique identifier for the message")
    ]
    text: Annotated[str, Field(..., description="Content of the message")]
    city: Annotated[
        Optional[str], Field(None, description="Provided city for the message")
    ] = None
    name: Annotated[
        Optional[str], Field(None, description="Provided name for the message")
    ] = None
