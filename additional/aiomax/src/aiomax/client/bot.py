from .session import MaxSession
from typing import TYPE_CHECKING, Optional
from ..methods.base import MaxMethod, ResponseT
from ..methods import Me
from ..types import BotInfo

if TYPE_CHECKING:
    from .session.base import BaseSession


class Bot:
    def __init__(self, token: str, session: Optional["BaseSession"] = None) -> None:
        self._session = session or MaxSession()
        self._token = token

    @property
    def token(self) -> str:
        return self._token

    async def __call__(self, method: MaxMethod[ResponseT]) -> ResponseT:
        """Executes the given method using the bot's session.

        Args:
            method (MaxMethod[ResponseT]): The method to execute.

        Returns:
            ResponseT: The response from the executed method.
        """
        return await self._session.request(method, self)

    async def me(self) -> BotInfo:
        """Retrieves information about the bot.

        Returns:
            BotInfo: Information about the bot.
        """
        return await self(Me())
