from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream import Context, ContextRepo
from faststream.security import SASLPlaintext
from importlib.metadata import version
from logging import Logger
from bot.bot import bot
from bot.notification_processor.handlers import moderation_result_router
from bot.utils import Config
from shared_models.messaging.queues.bot import (
    bot_message_shown_queue,
    bot_moderate_response_queue,
    bot_moderate_response_dlx_queue,
    bot_message_shown_dlx_queue,
)
from shared_models.messaging.exchanges import dlx_exchange, bot_exchange


broker = RabbitBroker(
    host=Config.RABBIT_HOST,
    port=Config.RABBIT_PORT,
    security=SASLPlaintext(
        username=Config.RABBIT_USER,
        password=Config.RABBIT_PASSWORD,
    ),
)

listener = broker.subscriber(bot_moderate_response_queue, bot_exchange)

app = FastStream(
    broker,
    title="Max bot notification processor",
    version=version("bot"),
    description="Notification processor for Max bot",
)
broker.include_router(moderation_result_router)


@app.on_startup
async def on_startup(context: ContextRepo):
    await broker.connect()
    await broker.declare_exchange(dlx_exchange)
    await broker.declare_exchange(bot_exchange)

    await broker.declare_queue(bot_moderate_response_queue)
    await broker.declare_queue(bot_moderate_response_dlx_queue)

    await broker.declare_queue(bot_message_shown_queue)
    await broker.declare_queue(bot_message_shown_dlx_queue)

    context.set_global("bot", bot)


@app.after_startup
async def after_startup(logger: Logger = Context()):
    logger.info(
        f"Max bot notification processor version {app.version} started successfully."
    )
