from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream import Context, ContextRepo
from faststream.security import SASLPlaintext
from importlib.metadata import version
from mistralai import Mistral
from logging import Logger
from auto_moderator.handlers import moderate_router
from shared_models.messaging.queues.auto_moderator import (
    auto_moderator_queue,
    auto_moderator_dlx_queue,
)
from shared_models.messaging.queues.bot import bot_moderate_response_queue
from shared_models.messaging.exchanges import (
    moderator_exchange,
    dlx_exchange,
    bot_exchange,
)
from .utils import Config


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
    title="Auto Moderator",
    version=version("auto_moderator"),
    description="A service for moderating messages in Facade Message Bot",
)
broker.include_router(moderate_router)


@app.on_startup
async def on_startup(context: ContextRepo):
    await broker.connect()
    await broker.declare_exchange(moderator_exchange)
    await broker.declare_exchange(dlx_exchange)
    await broker.declare_exchange(bot_exchange)

    await broker.declare_queue(auto_moderator_queue)
    await broker.declare_queue(auto_moderator_dlx_queue)
    await broker.declare_queue(bot_moderate_response_queue)

    context.set_global("mistral", Mistral(Config.MISTRAL_API_KEY))


@app.after_startup
async def after_startup(logger: Logger = Context()):
    logger.info(f"Auto Moderator version {app.version} started successfully.")
