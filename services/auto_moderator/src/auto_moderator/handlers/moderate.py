from faststream.rabbit import RabbitRouter
from logging import Logger
from shared_models.messaging.queues.auto_moderator import auto_moderator_queue
from shared_models.messaging.queues.manual_moderator import manual_moderator_queue
from shared_models.messaging.queues.bot import bot_moderate_response_queue
from shared_models.messaging.exchanges import moderator_exchange, bot_exchange
from shared_models.messaging import MessageInput, ModerationResult
from shared_models.enums import ModeratorType
from shared_models.enums import ModerationResult as ModerationResultEnum
from faststream import Context
from mistralai import Mistral


moderate_router = RabbitRouter()

manual_moderation = moderate_router.publisher(
    manual_moderator_queue, moderator_exchange
)


@moderate_router.publisher(bot_moderate_response_queue, bot_exchange)
@moderate_router.subscriber(auto_moderator_queue, moderator_exchange)
async def moderate(
    message_input: MessageInput,
    mistral: Mistral = Context(),
    logger: Logger = Context(),
) -> ModerationResult:
    logger.info(
        f"Received message {message_input.message.message_id} for moderation."
    )
    response = await mistral.classifiers.moderate_async(
        model="mistral-moderation-latest", inputs=[message_input.message.text]
    )
    if response.results[0].categories:
        failed_categories = [
            category
            for category in response.results[0].categories
            if response.results[0].categories[category]
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
        return result
    else:
        logger.warning(
            f"Moderation response for message {message_input.message.message_id} did not contain categories."
        )
        await manual_moderation.publish(message_input)
        return ModerationResult(
            message=message_input.message,
            source=ModeratorType.AUTO,
            result=ModerationResultEnum.APPROVED,
        )
