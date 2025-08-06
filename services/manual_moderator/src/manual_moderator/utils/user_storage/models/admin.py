from .base import UserStorageBaseModel
from typing import Annotated
from pydantic import Field


class Admin(UserStorageBaseModel):
    username: Annotated[
        str | None, Field(description="Username of the admin in Telegram")
    ] = None
    first_name: Annotated[str, Field(description="First name of the admin")]
    last_name: Annotated[
        str | None, Field(description="Last name of the admin", default=None)
    ] = None
