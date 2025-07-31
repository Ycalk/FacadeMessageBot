from faststream.rabbit import RabbitQueue, QueueType
from faststream.rabbit.schemas.queue import QuorumQueueArgs


auto_moderator_queue = RabbitQueue(
    "moderator.auto",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
    arguments=QuorumQueueArgs(
        {
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "dlx.moderator.auto",
            "x-dead-letter-strategy": "at-least-once",
        }
    ),
)

auto_moderator_dlx_queue = RabbitQueue(
    "dlx.moderator.auto",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
)
