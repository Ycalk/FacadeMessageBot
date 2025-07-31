from faststream.rabbit import RabbitQueue, QueueType
from faststream.rabbit.schemas.queue import QuorumQueueArgs


vision_notification_queue = RabbitQueue(
    "vision.notification",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
    arguments=QuorumQueueArgs(
        {
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "vision.notification.dlx",
            "x-dead-letter-strategy": "at-least-once",
        }
    ),
)

vision_notification_dlx_queue = RabbitQueue(
    "vision.notification.dlx",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
)
