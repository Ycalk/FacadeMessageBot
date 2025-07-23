import logging
from .session import MaxSession
from typing import TYPE_CHECKING, Optional
from ..methods.base import MaxMethod, ResponseT
from ..logging import get_logger
from ..methods import GetMe, GetUploadUrl
from ..types import InputFile, BotInfo

if TYPE_CHECKING:
    from .session.base import BaseSession


class Bot:
    def __init__(
        self,
        token: str,
        session: Optional["BaseSession"] = None,
        logging_level: int = logging.INFO,
    ) -> None:
        self._session = session or MaxSession()
        self._token = token
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
