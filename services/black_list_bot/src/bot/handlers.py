from aiomax.types.updates import MessageCreatedUpdate, BotStartedUpdate
from aiomax import Bot
from .utils import Config
from aiomax.methods import SendMessage
from .bot import broker, redis
from shared_models.messaging import (
    AddToBlackList,
    auto_moderator_black_list_queue,
    moderator_exchange,
)


async def message(update: MessageCreatedUpdate, bot: Bot) -> None:
    if not update.message or not update.message.sender or not update.message.body.text:
        return

    if (await redis.sismember("registered_users", update.message.sender.user_id)) == 0:  # type: ignore
        if update.message.body.text == Config.SECRET_KEY:
            await redis.sadd("registered_users", update.message.sender.user_id)  # type: ignore
            await bot(
                SendMessage(
                    user_id=update.message.sender.user_id,
                    text="Вы успешно зарегистрированы.\nВсе ваши сообщения будут автоматически добавляться в черный список.",
                )
            )
        else:
            await bot(
                SendMessage(
                    user_id=update.message.sender.user_id,
                    text="Введите секретный ключ.",
                )
            )
    else:
        await broker.publish(
            AddToBlackList(
                text=update.message.body.text,
            ),
            auto_moderator_black_list_queue,
            moderator_exchange,
        )
        await redis.sadd(
            f"user_black_list:{update.message.sender.user_id}", update.message.body.text
        )  # type: ignore
        await bot(
            SendMessage(
                user_id=update.message.sender.user_id,
                text="Ваше сообщение добавлено в черный список.",
            )
        )


async def start(update: BotStartedUpdate, bot: Bot) -> None:
    await bot(
        SendMessage(
            user_id=update.user.user_id,
            text=(
                "Отправьте секретный ключ для регистрации.\n"
                "После регистрации все ваши сообщения будут автоматически добавляться в черный список."
            ),
        )
    )
