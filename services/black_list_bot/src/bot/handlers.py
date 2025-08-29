from maxapi.types import MessageCreated, BotStarted
from maxapi import Bot
from .utils import Config
from .bot import broker, redis
from shared_models.messaging import (
    AddToBlackList,
    auto_moderator_black_list_queue,
    moderator_exchange,
)


async def message(event: MessageCreated) -> None:
    if not event.message or not event.message.sender or not event.message.body.text:
        return

    if (await redis.sismember("registered_users", event.message.sender.user_id)) == 0:  # type: ignore
        if event.message.body.text == Config.BLACK_LIST_BOT_SECRET_KEY:
            await redis.sadd("registered_users", event.message.sender.user_id)  # type: ignore
            await event.bot.send_message(
                user_id=event.message.sender.user_id,
                text="Вы успешно зарегистрированы.\nВсе ваши сообщения будут автоматически добавляться в черный список.",
            )
        else:
            await event.bot.send_message(
                user_id=event.message.sender.user_id,
                text="Введите секретный ключ.",
            )
    else:
        await broker.publish(
            AddToBlackList(
                text=event.message.body.text,
            ),
            auto_moderator_black_list_queue,
            moderator_exchange,
        )
        await redis.sadd(
            f"user_black_list:{event.message.sender.user_id}", event.message.body.text
        )  # type: ignore
        await event.bot.send_message(
            user_id=event.message.sender.user_id,
            text="Ваше сообщение добавлено в черный список.",
        )


async def start(event: BotStarted) -> None:
    await event.bot.send_message(
        user_id=event.user.user_id,
        text=(
            "Отправьте секретный ключ для регистрации.\n"
            "После регистрации все ваши сообщения будут автоматически добавляться в черный список."
        ),
    )
