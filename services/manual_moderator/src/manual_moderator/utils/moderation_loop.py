import asyncio
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .user_storage import BotData, Moderator
from .config import Config
from .texts import Texts
from datetime import datetime


class ModerationLoop:
    def __init__(self, bot: Bot, iteration_delay: float = 0.1):
        self.bot = bot
        self.iteration_delay = iteration_delay
        self.inactive_timeout = Config.INACTIVITY_TIMEOUT_MINUTES * 60

    async def _check_for_activity(self, moderators: list[Moderator]) -> None:
        current_time = int(datetime.now(tz=Config.TIME_ZONE).timestamp())
        for moderator in moderators:
            if not moderator.last_activity:
                continue
            if (
                moderator.is_active
                and moderator.processing_message
                and (current_time - moderator.last_activity > self.inactive_timeout)
            ):
                await moderator.mark_inactive()
                await self.bot.send_message(
                    moderator.telegram_id, Texts.Messages.marked_as_inactive
                )

    async def start(self) -> None:
        while True:
            await asyncio.sleep(self.iteration_delay)
            moderators = await Moderator.all()
            if len(moderators) == 0:
                continue

            await self._check_for_activity(moderators)

            message = await BotData.get_new_processing_message()
            if not message:
                continue

            chosen_moderator = moderators[message.message_id % len(moderators)]
            await self.bot.send_message(
                chosen_moderator.telegram_id,
                Texts.Messages.new_message_for_moderation.format(
                    text=message.text,
                    name=message.name,
                    city=message.city,
                ),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Утвердить",
                                callback_data=f"approve:{message.message_id}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="Отклонить",
                                callback_data=f"reject:{message.message_id}",
                            )
                        ],
                    ]
                ),
            )
