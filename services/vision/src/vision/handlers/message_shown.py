from faststream.rabbit import RabbitRouter
from logging import Logger
from shared_models.messaging.queues.vision import (
    vision_notification_queue,
    vision_notification_dlx_queue,
)
from shared_models.messaging.exchanges import (
    vision_exchange,
    dlx_exchange,
)
from vision.utils.storage.base import BaseStorage
from vision.utils.storage.models import ShownMessage
from shared_models.messaging import MessageInput
from uuid import uuid4
from datetime import datetime
from faststream import Context


message_shown_router = RabbitRouter()

dlx = message_shown_router.publisher(vision_notification_dlx_queue, dlx_exchange)


@message_shown_router.subscriber(vision_notification_queue, vision_exchange)
async def moderate(
    message_input: MessageInput,
    logger: Logger = Context(),
    storage: BaseStorage = Context(),
):
    logger.info(f"Received shown message {message_input.message.message_id}.")
    await storage.save_shown_message(
        ShownMessage(
            message=message_input.message,
            id=uuid4(),
            show_at=datetime.now(),
        )
    )
