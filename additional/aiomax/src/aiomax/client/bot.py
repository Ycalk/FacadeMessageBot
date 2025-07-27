from inspect import get_annotations
import logging
import asyncio
import traceback
from .session import MaxSession
from typing import TYPE_CHECKING, Optional, AsyncGenerator
from ..methods.base import MaxMethod, ResponseT
from ..logging import get_logger
from ..methods import GetMe, GetUploadUrl, GetUpdates
from ..types import InputFile, BotInfo, Update
from typing import (
    Callable,
    TypeVar,
    Generic,
    Awaitable,
    get_type_hints,
    get_args,
    Union,
)
from dataclasses import dataclass

if TYPE_CHECKING:
    from .session.base import BaseSession

from ..types.models.update.base import UpdateBase

UpdateT = TypeVar("UpdateT", bound=UpdateBase)


@dataclass(frozen=True)
class _Handler(Generic[UpdateT]):
    handler: Callable[[UpdateT, "Bot"], Awaitable[None]]
    filter: Union[Callable[[UpdateT], bool], Callable[[UpdateT], Awaitable[bool]]]


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
        self._stop_event = asyncio.Event()
        self._handlers: dict[str, list[_Handler]] = {}
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
        handler: Callable[[UpdateT, "Bot"], Awaitable[None]],
        filter: Union[
            Callable[[UpdateT], bool], Callable[[UpdateT], Awaitable[bool]]
        ] = lambda _: True,
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
        if key not in self._handlers:
            self._handlers[key] = []
        self._handlers[key].append(_Handler[UpdateT](handler, filter))

    async def _listen_for_updates(
        self, timeout: int, sleep_on_exception: int
    ) -> AsyncGenerator[Update, None]:
        while True:
            try:
                updates = await self(GetUpdates(timeout=timeout))
            except Exception as _:
                self.logger.error(
                    f"Error while fetching updates\n:{traceback.format_exc()}"
                )
                self.logger.info(f"Retrying in {sleep_on_exception} seconds...")
                await asyncio.sleep(sleep_on_exception)
                continue
            for update in updates.updates:
                self.logger.debug(f"Received update: {update}")
                yield update

    async def start_polling(
        self, timeout: int = 20, sleep_on_exception: int = 1
    ) -> None:
        """Starts polling for updates from the Max API.

        Args:
            timeout (int, optional): The timeout for each request in seconds. Defaults to 20.
            sleep_on_exception (int, optional): The time to wait before retrying after an exception in seconds. Defaults to 1.
        """
        self.logger.info(f"Starting polling for updates with timeout {timeout}s")
        me = await self.me()
        self.logger.info(f"Bot: {me}")
        self.logger.info("Registered handlers:\n")
        for key, handlers in self._handlers.items():
            self.logger.info(f"  {key}:")
            for handler in handlers:
                self.logger.info(
                    f"    - {handler.handler.__name__} (filter: {handler.filter.__name__})"
                )
        async for update in self._listen_for_updates(timeout, sleep_on_exception):
            update_type = update.update_type
            self.logger.debug(f"Processing update of type: {update_type}")

            if update_type not in self._handlers:
                self.logger.warning(
                    f"No handlers registered for update type: {update_type}"
                )
                continue

            for handler in self._handlers[update_type]:
                filter_result = handler.filter(update)
                if asyncio.iscoroutine(filter_result):
                    filter_result = await filter_result
                if filter_result:
                    try:
                        self.logger.debug(
                            f"Calling handler: {handler.handler.__name__}"
                        )
                        await handler.handler(update, self)
                        break
                    except Exception as _:
                        self.logger.error(
                            f"Error while processing update with handler {handler.handler.__name__}\n:{traceback.format_exc()}"
                        )
            else:
                self.logger.warning(
                    f"No handler processed update of type: {update_type} with content: {update}"
                )
