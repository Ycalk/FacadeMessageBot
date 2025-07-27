from ...base import MaxMethod
from ....types import BotInfo


class GetMe(MaxMethod[BotInfo]):
    """Get information about the bot."""

    @property
    def endpoint(self) -> str:
        return "/me"

    @property
    def method(self) -> str:
        return "GET"

    def load_response(self, json_data: str | bytes | bytearray) -> BotInfo:
        return BotInfo.model_validate_json(json_data)
