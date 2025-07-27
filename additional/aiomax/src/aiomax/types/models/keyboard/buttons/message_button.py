from .base import KeyboardButtonBase
from typing import Literal


class MessageButton(KeyboardButtonBase):
    type: Literal["message"] = "message"
