import asyncio
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream import Context, ContextRepo
from faststream.security import SASLPlaintext
from importlib.metadata import version
from logging import Logger
from .utils import Config, RedisStorage
from redis.asyncio import Redis
from shared_models.messaging import bot_exchange, bot_message_shown_queue
from .handlers import message_shown_router


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
    title="Vision",
    version=version("vision"),
    description="A service for watching video stream.",
)

bot_publisher = broker.publisher(bot_message_shown_queue, bot_exchange)
broker.include_router(message_shown_router)

on_startup_finished_event = asyncio.Event()


@app.on_startup
async def on_startup(context: ContextRepo):
    redis = Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DATA_STORAGE_DB,
    )
    storage = RedisStorage(redis)
    context.set_global("redis", redis)
    context.set_global("storage", storage)


@app.after_startup
async def after_startup(logger: Logger = Context()):
    logger.info(f"Vision version {app.version} started successfully.")
    on_startup_finished_event.set()
