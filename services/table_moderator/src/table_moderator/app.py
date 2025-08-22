import asyncio
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream import Context, ContextRepo
from faststream.security import SASLPlaintext
from importlib.metadata import version
from logging import Logger
from .utils import Config, Sheet, Storage
from .handlers import moderate_router
from shared_models.messaging.queues.facade_message_moderator import (
    facade_message_moderator_queue,
)
from shared_models.messaging.queues.bot import bot_moderate_response_queue
from shared_models.messaging.exchanges import moderator_exchange, bot_exchange


broker = RabbitBroker(
    host=Config.RABBIT_HOST,
    port=Config.RABBIT_PORT,
    security=SASLPlaintext(
        username=Config.RABBIT_USER,
        password=Config.RABBIT_PASSWORD,
    ),
)

app = FastStream(
    broker,
    title="Table Moderator",
    version=version("table_moderator"),
    description="A service for moderating messages in Facade Message Bot",
)

broker.include_router(moderate_router)

facade_message_publisher = broker.publisher(
    facade_message_moderator_queue,
    moderator_exchange,
)
bot_publisher = broker.publisher(
    bot_moderate_response_queue,
    bot_exchange,
)

startup_complete_event = asyncio.Event()


@app.on_startup
async def on_startup(context: ContextRepo):
    context.set_global("sheet", Sheet())
    context.set_global("storage", Storage())


@app.after_startup
async def after_startup(logger: Logger = Context()):
    logger.info(f"Table Moderator version {app.version} started successfully.")
    startup_complete_event.set()
