import asyncio
from logging import Logger
from .sheet import Sheet, SheetMessage
from .storage import Storage
from faststream.rabbit.publisher.asyncapi import AsyncAPIPublisher
from shared_models.messaging import ModerationResult, Message, MessageInput
from shared_models.enums import ModeratorType
from shared_models.enums import ModerationResult as ModerationResultEnum


class UpdateLoop:
    def __init__(
        self,
        sheet: Sheet,
        logger: Logger,
        facade_message_publisher: AsyncAPIPublisher,
        storage: Storage,
        bot_publisher: AsyncAPIPublisher,
    ):
        self.sheet = sheet
        self.storage = storage
        self.facade_message_publisher = facade_message_publisher
        self.bot_publisher = bot_publisher
        self.logger = logger

    async def send_message(self, sheet_message: SheetMessage, storage_message: Message):
        await self.bot_publisher.publish(
            ModerationResult(
                message=storage_message,
                source=ModeratorType.TABLE,
                result=ModerationResultEnum.APPROVED
                if sheet_message.approved
                else ModerationResultEnum.REJECTED,
            )
        )
        if sheet_message.approved:
            await self.facade_message_publisher.publish(
                MessageInput(message=storage_message)
            )
        self.logger.info(f"Message {sheet_message.message_id} processed.")

    async def start(self):
        self.logger.info("Starting update loop...")
        while True:
            try:
                sheet_messages = await self.sheet.parse_messages()
                for sheet_message in sheet_messages:
                    storage_message = await self.storage.get_message(
                        sheet_message.message_id
                    )
                    if sheet_message.approved is None or storage_message is None:
                        continue
                    await self.send_message(sheet_message, storage_message)
                    await self.storage.delete_message(sheet_message.message_id)
                    await self.sheet.mark_as_processed(sheet_message.index)
                await asyncio.sleep(5)
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(5)
