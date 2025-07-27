from .base import KeyboardButtonBase
from ....base import UNSET, UNSET_TYPE
from typing import Literal
from pydantic import Field


class OpenAppButton(KeyboardButtonBase):
    type: Literal["open_app"] = "open_app"
    web_app: str | UNSET_TYPE = Field(
        UNSET, description="Web app URL to open when the button is clicked"
    )
    contact_id: int | UNSET_TYPE = Field(
        UNSET, description="Bot ID to open the app for"
    )
