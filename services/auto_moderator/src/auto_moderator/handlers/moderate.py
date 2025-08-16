from faststream.rabbit import RabbitRouter
from logging import Logger
from auto_moderator.utils import Config, BlackList
from shared_models.messaging.queues.auto_moderator import (
    auto_moderator_queue,
    auto_moderator_dlx_queue,
)
from shared_models.messaging.queues.manual_moderator import manual_moderator_queue
from shared_models.messaging.queues.bot import bot_moderate_response_queue
from shared_models.messaging.exchanges import (
    moderator_exchange,
    bot_exchange,
    dlx_exchange,
)
from shared_models.messaging import MessageInput, ModerationResult, ModerationError
from shared_models.enums import ModeratorType
from shared_models.enums import ModerationResult as ModerationResultEnum
from faststream import Context
from mistralai import Mistral


moderate_router = RabbitRouter()

manual_moderation = moderate_router.publisher(
    manual_moderator_queue, moderator_exchange
)
bot_moderate_response = moderate_router.publisher(
    bot_moderate_response_queue, bot_exchange
)
dlx = moderate_router.publisher(auto_moderator_dlx_queue, dlx_exchange)


@moderate_router.subscriber(auto_moderator_queue, moderator_exchange)
async def moderate(
    message_input: MessageInput,
    mistral: Mistral = Context(),
    logger: Logger = Context(),
    black_list: BlackList = Context(),
):
    logger.info(f"Received message {message_input.message.message_id} for moderation.")
    if black_list.is_blacklisted(message_input.message.text):
        logger.info(
            f"Message {message_input.message.message_id} is blacklisted, skipping moderation."
        )
        result = ModerationResult(
            message=message_input.message,
            source=ModeratorType.AUTO,
            result=ModerationResultEnum.REJECTED,
            reason="Blacklisted word detected",
        )
        await bot_moderate_response.publish(result)
        return

    response = await mistral.classifiers.moderate_async(
        model="mistral-moderation-latest", inputs=[message_input.message.text]
    )
    if response.results[0].category_scores:
        failed_categories = [
            category
            for category in response.results[0].category_scores
            if response.results[0].category_scores[category]
            > Config.MAXIMAL_CATEGORY_SCORE_FOR_APPROVE
        ]
        result = ModerationResult(
            message=message_input.message,
            source=ModeratorType.AUTO,
            result=ModerationResultEnum.APPROVED
            if len(failed_categories) == 0
            else ModerationResultEnum.REJECTED,
            reason=",".join(failed_categories) if failed_categories else None,
        )
        if result.result == ModerationResultEnum.APPROVED:
            await manual_moderation.publish(message_input)
        logger.info(
            f"Moderation result for message {message_input.message.message_id}: {result.result}, "
            f"reason: {result.reason}"
        )
        await bot_moderate_response.publish(result)
    else:
        logger.error(
            f"Moderation response for message {message_input.message.message_id} did not contain categories."
        )
        await manual_moderation.publish(message_input)
        await dlx.publish(
            ModerationError(
                message=message_input.message,
                exception="Moderation response did not contain categories",
            )
        )
