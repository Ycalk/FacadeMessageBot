import asyncio
import logging
import html
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .user_storage import BotData, Moderator
from .config import Config
from .texts import Texts
from .user_storage import UserStorage
from shared_models.messaging import ModerationResult, MessageInput
from shared_models.messaging.queues.bot import bot_moderate_response_queue
from shared_models.messaging.exchanges import bot_exchange, moderator_exchange
from shared_models.messaging.queues.table_moderator import (
    table_moderator_queue,
)
from shared_models.enums import ModeratorType
from shared_models.enums import ModerationResult as ModerationResultEnum
from datetime import datetime


class ModerationLoop:
    def __init__(self, bot: Bot, iteration_delay: float = 0.1):
        self.bot = bot
        self.iteration_delay = iteration_delay
        self.inactive_timeout = Config.INACTIVITY_TIMEOUT_MINUTES * 60

    async def _check_for_activity(self) -> None:
        current_time = int(datetime.now(tz=Config.TIME_ZONE).timestamp())
        moderators = await Moderator.all()

        for moderator in moderators:
            if not moderator.message_processing_start:
                continue
            if (
                moderator.is_active
                and moderator.processing_message
                and (
                    current_time - moderator.message_processing_start
                    > self.inactive_timeout
                )
            ):
                await moderator.mark_inactive()
                await self.bot.send_message(
                    moderator.telegram_id, Texts.Messages.marked_as_inactive
                )

    async def _auto_approve_messages(self) -> None:
        message = await BotData.get_new_processing_message()
        while message:
            await UserStorage.broker.publish(
                ModerationResult(
                    message=message,
                    source=ModeratorType.MANUAL,
                    result=ModerationResultEnum.APPROVED,
                    reason="Auto-approve is enabled.",
                ),
                bot_moderate_response_queue,
                bot_exchange,
            )
            await UserStorage.broker.publish(
                MessageInput(
                    message=message,
                ),
                table_moderator_queue,
                moderator_exchange,
            )
            message = await BotData.get_new_processing_message()

    async def start(self) -> None:
        logger = logging.getLogger(__name__)
        logger.info("Starting moderation loop")
        while True:
            try:
                await asyncio.sleep(self.iteration_delay)
                # Uncomment the following line to enable inactivity checks
                # await self._check_for_activity()

                moderators = [
                    moderator
                    for moderator in await Moderator.all()
                    if moderator.is_active and not moderator.processing_message
                ]

                if await BotData.is_auto_approve_enabled():
                    await self._auto_approve_messages()
                    continue

                if len(moderators) == 0:
                    continue

                message = await BotData.get_new_processing_message()

                if not message:
                    continue

                chosen_moderator = moderators[message.message_id % len(moderators)]
                chosen_moderator.processing_message = message
                chosen_moderator.message_processing_start = int(
                    datetime.now(tz=Config.TIME_ZONE).timestamp()
                )

                await chosen_moderator.save()
                await self.bot.send_message(
                    chosen_moderator.telegram_id,
                    Texts.Messages.new_message_for_moderation.format(
                        text=html.escape(message.text),
                        name=html.escape(message.name),
                        city=html.escape(message.city),
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
            except Exception as e:
                logger.error(f"Error in moderation loop: {e}", exc_info=True)
