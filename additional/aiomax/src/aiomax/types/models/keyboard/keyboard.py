from ...base import MaxObject
from .buttons import KeyboardButton


class Keyboard(MaxObject):
    buttons: list[list[KeyboardButton]]
