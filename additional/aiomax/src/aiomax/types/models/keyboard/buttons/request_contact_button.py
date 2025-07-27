from .base import KeyboardButtonBase
from typing import Literal


class RequestContactButton(KeyboardButtonBase):
    type: Literal["request_contact"] = "request_contact"
