from faststream.rabbit import RabbitRouter
from logging import Logger
from auto_moderator.utils import BlackList
from shared_models.messaging.queues.auto_moderator import (
    auto_moderator_black_list_dlx_queue,
    auto_moderator_black_list_queue,
)
from shared_models.messaging.exchanges import (
    moderator_exchange,
    dlx_exchange,
)
from shared_models.messaging import AddToBlackList, ErrorResponse
from faststream import Context


add_to_black_list_router = RabbitRouter()

dlx = add_to_black_list_router.publisher(
    auto_moderator_black_list_dlx_queue, dlx_exchange
)


@add_to_black_list_router.subscriber(
    auto_moderator_black_list_queue, moderator_exchange
)
async def moderate(
    request: AddToBlackList,
    logger: Logger = Context(),
    black_list: BlackList = Context(),
):
    logger.info(f"Adding message {request.text} to black list.")
    try:
        await black_list.add_to_blacklist(request.text)
    except Exception as e:
        logger.error(f"Failed to add message to black list: {e}")
        await dlx.publish(
            ErrorResponse(
                exception=str(e),
                details=f"Failed to add '{request.text}' to black list.",
            )
        )
        return
