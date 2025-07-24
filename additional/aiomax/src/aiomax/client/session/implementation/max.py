from typing import TYPE_CHECKING
from ..base import BaseSession, DEFAULT_TIMEOUT
from aiomax.types import InputFile, UploadType
from ....methods.base import MaxMethod, ResponseT
from ....exceptions import (
    DecodeModelError,
    BadRequestError,
    MethodNotAllowedError,
    NotFoundError,
    UnauthorizedError,
    ServiceUnavailableError,
    TooManyRequestsError,
    APIError,
)
from typing import Final
from httpx import AsyncClient

if TYPE_CHECKING:
    from aiomax.client.bot import Bot

BASE_URL: Final[str] = "https://botapi.max.ru"


class MaxSession(BaseSession):
    """MaxSession is a session implementation for interacting with the Max API."""

    def __init__(
        self, timeout: float = DEFAULT_TIMEOUT, base_url: str = BASE_URL
    ) -> None:
        super().__init__(timeout)
        self.base_url = base_url

    def _validate_response(
        self, method: MaxMethod[ResponseT], status: int, content: str
    ) -> ResponseT:
        match status:
            case 200:
                try:
                    return method.load_response(content)
                except Exception as e:
                    raise DecodeModelError(e, type(method), content)
            case 400:
                raise BadRequestError(type(method), content)
            case 401:
                raise UnauthorizedError(type(method), content)
            case 404:
                raise NotFoundError(type(method), content)
            case 405:
                raise MethodNotAllowedError(type(method), content)
            case 429:
                raise TooManyRequestsError(type(method), content)
            case 503:
                raise ServiceUnavailableError(type(method), content)
            case _:
                raise APIError(status, type(method), content, "Unknown error")

    async def request(self, method: MaxMethod[ResponseT], bot: "Bot") -> ResponseT:
        """Create and send a request to the Max API.

        Args:
            method (MaxMethod[ResponseT]): The method to be executed.
            bot (Bot): The bot instance containing the token.

        Returns:
            ResponseT: The response from the Max API, validated and parsed.
        """
        parameters = method.query_parameters.copy()
        parameters["access_token"] = bot.token
        async with AsyncClient(base_url=self.base_url, timeout=self._timeout) as client:
            response = await client.request(
                method=method.method,
                url=method.endpoint,
                params=parameters,
                json=method.body,
            )
            return self._validate_response(method, response.status_code, response.text)

    async def upload(self, file: InputFile, url: str, bot: "Bot") -> str | None:
        async with AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                url, files={"data": (file.filename, file.data, file.upload_type.value)}
            )
        if response.status_code != 200:
            raise APIError(
                response.status_code,
                type(MaxSession.upload),
                response.text,
                "Failed to upload",
            )
        if file.upload_type in (UploadType.VIDEO, UploadType.AUDIO):
            return None
        try:
            return next(iter(response.json()["photos"].values()))["token"]
        except Exception as e:
            raise DecodeModelError(e, type(MaxSession.upload), response.text) from e
