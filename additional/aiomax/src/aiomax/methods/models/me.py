from ..base import MaxMethod
from ...types import BotInfo


class Me(MaxMethod[BotInfo]):
    @property
    def endpoint(self) -> str:
        return "/me"

    @property
    def method(self) -> str:
        return "GET"
