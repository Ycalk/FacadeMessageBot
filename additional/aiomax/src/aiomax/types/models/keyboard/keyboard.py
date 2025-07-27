from ...base import MaxObject
from .buttons import KeyboardButton
from typing import Sequence


class Keyboard(MaxObject):
    buttons: list[Sequence[KeyboardButton]]
