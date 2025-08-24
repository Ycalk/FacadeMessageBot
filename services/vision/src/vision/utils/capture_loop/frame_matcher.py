import asyncio
from shared_models.messaging import MessageShown as MessageShownSharedModel
from faststream.rabbit.publisher.asyncapi import AsyncAPIPublisher
from thefuzz import process
from datetime import datetime, timedelta
from logging import Logger
from ..config import Config
from ..storage.base import BaseStorage
from ..storage.models import Image, ShownMessage


class FrameMatcher:
    def __init__(
        self, storage: BaseStorage, logger: Logger, bot_publisher: AsyncAPIPublisher
    ) -> None:
        self.storage = storage
        self.logger = logger
        self.publisher = bot_publisher

    async def start(self):
        self.logger.info("Starting frame matcher loop...")

        while True:
            try:
                await asyncio.sleep(1)
                await self.match_frames()
            except KeyboardInterrupt:
                self.logger.info("Frame matcher interrupted by user.")
                return
            except Exception as e:
                self.logger.error(f"Error in frame matcher loop: {e}")
                await asyncio.sleep(1)
                continue

    async def match_frames(self) -> None:
        current_time = datetime.now()
        shown_messages = await self.storage.find_shown_messages_by_show_at_time(
            start=datetime(1970, 1, 1),
            end=current_time - timedelta(seconds=Config.ANALYTICS_DELAY_SECONDS),
        )
        images = await self.storage.find_images_by_created_time(
            start=current_time
            - timedelta(seconds=Config.MAXIMUM_IMAGE_STORAGE_TIME_SECONDS),
            end=current_time,
        )
        for shown_message in shown_messages:
            matched_image: Image = process.extractOne(
                "".join(
                    [
                        "".join(shown_message.message.name.split()).lower(),
                        "".join(shown_message.message.city.split()).lower(),
                        "".join(shown_message.message.text.split()).lower(),
                    ]
                ),
                choices=images,
            )[0]
            self.logger.info(
                f"Matching shown message {shown_message.message.message_id} with image {matched_image.id}"
            )
            self.logger.info(
                f"Message text: {shown_message.message.text}\nImage text: {matched_image.text}"
            )
            await self.send_shown_message(shown_message, matched_image)
            await self.storage.delete_shown_message(shown_message)
            await self.storage.delete_image(matched_image)

        await self.storage.delete_old_images(
            current_time - timedelta(seconds=Config.MAXIMUM_IMAGE_STORAGE_TIME_SECONDS)
        )
        deleted_messages = await self.storage.delete_old_shown_messages(
            current_time - timedelta(seconds=Config.MAXIMUM_IMAGE_STORAGE_TIME_SECONDS)
        )
        for message in deleted_messages:
            self.logger.error(
                "Cannot find image for shown message: %s", message.message.message_id
            )
            await self.send_shown_message(message, None)

    async def send_shown_message(
        self, shown_message: ShownMessage, image: Image | None
    ) -> None:
        self.logger.info(f"Sending shown message {shown_message.message.message_id}")
        await self.publisher.publish(
            MessageShownSharedModel(
                message=shown_message.message,
                photo_base64=image.image_base64 if image else None,
            )
        )
