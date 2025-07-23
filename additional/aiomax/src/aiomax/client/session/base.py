from abc import ABC, abstractmethod
from typing import Final, TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot
    from ...methods.base import MaxMethod, ResponseT

DEFAULT_TIMEOUT: Final[float] = 30.0


class BaseSession(ABC):
    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        self._timeout = timeout

    @abstractmethod
    async def request(self, method: "MaxMethod[ResponseT]", bot: "Bot") -> "ResponseT":
        """Executes the method and returns the response.

        Args:
            method (MaxMethod[ResponseT]): The method to be executed.
            bot (Bot): The bot instance to use for the request.

        Returns:
            ResponseT: The response from the method.
        """
        ...

    async def __call__(self, method: "MaxMethod[ResponseT]", bot: "Bot") -> "ResponseT":
        """Executes the method and returns the response.

        Args:
            method (MaxMethod[ResponseT]): The method to be executed.
            bot (Bot): The bot instance to use for the request.

        Returns:
            ResponseT: The response from the method.
        """
        return await self.request(method, bot)
