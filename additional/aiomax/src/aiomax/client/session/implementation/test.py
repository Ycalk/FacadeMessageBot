from ..base import BaseSession
from ....methods.base import MaxMethod, ResponseT
from ....methods import GetUpdates
from ....types import InputFile, Update, UpdateList
from ..base import DEFAULT_TIMEOUT
from typing import TYPE_CHECKING, Generic, Sequence, Type
from dataclasses import dataclass
from asyncio import Queue

if TYPE_CHECKING:
    from aiomax.client.bot import Bot


@dataclass
class TestResponse(Generic[ResponseT]):
    """A dataclass to hold test responses for methods."""

    method: Type[MaxMethod[ResponseT]]
    response: ResponseT


class TestSession(BaseSession):
    """Test session for aiomax client."""

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT,
        responses: Sequence[TestResponse] = [],
    ) -> None:
        super().__init__(timeout)
        self.update_queue: Queue[Update] = Queue()
        self.requests: list[MaxMethod] = []
        self.responses = responses

    async def add_update(self, update: Update, clear_requests: bool = True) -> None:
        """Add an update to the session's update queue.

        Args:
            update (GetUpdates): The update to add to the queue.
            clear_requests (bool): Whether to clear the requests list before adding the update.
        """
        if clear_requests:
            self.requests.clear()
        await self.update_queue.put(update)

    async def request(self, method: MaxMethod[ResponseT], bot: "Bot") -> ResponseT:
        if isinstance(method, GetUpdates):
            update = await self.update_queue.get()
            return UpdateList(updates=[update], marker=None)  # type: ignore
        self.requests.append(method)
        result = next(
            (res for res in self.responses if isinstance(method, res.method)),
            None,
        )
        if result is None:
            raise ValueError(f"No test response for method {method}")
        return result.response

    async def upload(self, file: InputFile, url: str, bot: "Bot") -> str | None:
        raise NotImplementedError(
            "Upload functionality is not implemented in TestSession. "
        )
