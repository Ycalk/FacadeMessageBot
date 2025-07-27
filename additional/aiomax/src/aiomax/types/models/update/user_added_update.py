from .base import UpdateBase
from pydantic import Field
from typing import Literal
from ..user import User


class UserAddedUpdate(UpdateBase):
    update_type: Literal["user_added"] = "user_added"
    chat_id: int = Field(..., description="ID of the chat where the user was added")
    user: User = Field(..., description="User who was added")
    inviter_id: int | None = Field(
        None, description="ID of the user who invited the new user, if available"
    )
    is_channel: bool = Field(
        ..., description="True if the user was added to a channel, False if to a group"
    )
