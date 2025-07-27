from .user_with_photo import UserWithPhoto
from ..bot_command import BotCommand
from pydantic import Field


class BotInfo(UserWithPhoto):
    commands: list[BotCommand] | None = Field(
        None,
        description="A list of bot commands. If the bot doesn't have any commands, the field is empty.",
    )
