from ...base import MaxObject
from typing import Literal
from ..keyboard import Keyboard


class InlineKeyboardAttachment(MaxObject):
    type: Literal["inline_keyboard"] = "inline_keyboard"
    payload: Keyboard
