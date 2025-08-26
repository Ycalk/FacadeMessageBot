from shared_models.database import User, Message
from shared_models.enums import MessageState
from .config import Config
from datetime import datetime


async def messages_limit_reached(max_id: int) -> bool:
    user = await User.get_or_none(max_id=max_id)
    if not user:
        return True

    messages_count = (
        await Message.filter(user=user).exclude(state=MessageState.REJECTED).count()
    )

    # TODO: Add admin ids?
    # if max_id == 5472490:
    #     return False

    return messages_count >= Config.MAXIMUM_MESSAGES_PER_USER


async def attempts_limit_reached(max_id: int) -> bool:
    user = await User.get_or_none(max_id=max_id)
    if not user:
        return True

    messages = await Message.filter(user=user).order_by("created_at")
    remaining_attempts = Config.MAXIMUM_ATTEMPTS_PER_MESSAGE
    for message in messages:
        if message.state == MessageState.REJECTED:
            remaining_attempts -= 1
        else:
            remaining_attempts = Config.MAXIMUM_ATTEMPTS_PER_MESSAGE
        if remaining_attempts <= 0:
            return True
    return False


async def messages_time_out_reached(max_id: int) -> bool:
    user = await User.get_or_none(max_id=max_id)
    if not user:
        return True

    messages = await Message.filter(user=user).order_by("created_at")
    if len(messages) == 0:
        return False

    last_message = messages[-1]
    time_since_last_message = (
        datetime.now(last_message.created_at.tzinfo) - last_message.created_at
    ).total_seconds() / 60.0
    return time_since_last_message < Config.MESSAGES_TIME_OUT_MINUTES
