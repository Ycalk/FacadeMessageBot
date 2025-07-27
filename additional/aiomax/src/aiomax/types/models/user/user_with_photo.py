from .user import User
from pydantic import Field


class UserWithPhoto(User):
    description: str | None = Field(None, description="Description of the user")
    avatar_url: str | None = Field(None, description="URL of the user's avatar")
    full_avatar_url: str | None = Field(
        None, description="URL of the user's bigger avatar"
    )
