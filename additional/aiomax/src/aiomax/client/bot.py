from inspect import get_annotations
import logging
from .session import MaxSession
from typing import TYPE_CHECKING, Optional
from ..methods.base import MaxMethod, ResponseT
from ..logging import get_logger
from ..methods import GetMe, GetUploadUrl
from ..types import InputFile, BotInfo
from typing import Callable, TypeVar, Generic, Awaitable, get_type_hints, get_args
from dataclasses import dataclass

if TYPE_CHECKING:
    from .session.base import BaseSession

from ..types.models.update.base import UpdateBase

UpdateT = TypeVar("UpdateT", bound=UpdateBase)


@dataclass(frozen=True)
class _Handler(Generic[UpdateT]):
    handler: Callable[[UpdateT], Awaitable[None]]
    filter: Callable[[UpdateT], bool]


class Bot:
    """A class representing a bot that interacts with the Max API."""

    def __init__(
        self,
        token: str,
        session: Optional["BaseSession"] = None,
        logging_level: int = logging.INFO,
    ) -> None:
        """Initializes the Bot instance.

        Args:
            token (str): The bot's token for authentication.
            session (Optional[&quot;BaseSession&quot;], optional): The session to use for API requests. Defaults to MaxSession.
            logging_level (int, optional): The logging level for the bot's logger. Defaults to logging.INFO.
        """
        self._session = session or MaxSession()
        self._token = token
        self._handlers: dict[str, _Handler] = {}
        self.logger = get_logger("aiomax.bot", level=logging_level)

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
        self.logger.debug(
            f"Executing method: {method.__class__.__name__} with params: {method}"
        )
        result = await self._session.request(method, self)
        self.logger.debug(f"Method result:\n{result}")
        return result

    async def me(self) -> BotInfo:
        """Retrieves information about the bot.

        Returns:
            BotInfo: Information about the bot.
        """
        return await self(GetMe())

    async def upload(self, file: InputFile) -> str:
        """Uploads a file to the Max API.

        Args:
            file (InputFile): The file to upload.

        Returns:
            str: Token of the uploaded file.
        """
        self.logger.debug(f"Uploading file: {file.filename}")
        upload_url = await self(GetUploadUrl(type=file.upload_type))
        result = await self._session.upload(file, upload_url.url, self)

        token = result or upload_url.token
        if not isinstance(token, str):
            raise ValueError("Upload did not return a valid token.")
        self.logger.debug(f"File uploaded successfully, token: {token}")

        return token

    def register_handler(
        self,
        handler: Callable[[UpdateT], Awaitable[None]],
        filter: Callable[[UpdateT], bool] = lambda _: True,
    ) -> None:
        handler_type_hints = get_type_hints(handler)
        update_type = handler_type_hints.get("update") or next(
            iter(handler_type_hints.values()), None
        )

        if not update_type:
            raise ValueError("Cannot infer update type from handler")

        update_annotations = get_annotations(update_type)
        if not update_annotations or "update_type" not in update_annotations:
            raise ValueError("Update type incorrect")

        key = get_args(update_annotations["update_type"])[0]
        self._handlers[key] = _Handler[UpdateT](handler, filter)
