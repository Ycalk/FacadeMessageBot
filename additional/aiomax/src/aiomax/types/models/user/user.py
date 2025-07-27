from ...base import MaxObject
from pydantic import Field


class User(MaxObject):
    user_id: int = Field(..., description="Unique identifier for the user")
    first_name: str = Field(..., description="First name of the user")
    last_name: str | None = Field(None, description="Last name of the user")
    username: str | None = Field(None, description="Username of the user")
    is_bot: bool = Field(..., description="Indicates if the user is a bot")
    last_activity_time: int = Field(
        ..., description="Timestamp of the user's last activity"
    )
