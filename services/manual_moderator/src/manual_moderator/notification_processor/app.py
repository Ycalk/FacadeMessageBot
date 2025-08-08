from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream import Context, ContextRepo
from faststream.security import SASLPlaintext
from importlib.metadata import version
from logging import Logger
from manual_moderator.bot import bot
from manual_moderator.notification_processor.handlers import moderate_router
from manual_moderator.utils import Config


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
    title="Moderator bot notification processor",
    version=version("manual_moderator"),
    description="Notification processor for moderator bot",
)
broker.include_router(moderate_router)


@app.on_startup
async def on_startup(context: ContextRepo):
    context.set_global("bot", bot)


@app.after_startup
async def after_startup(logger: Logger = Context()):
    logger.info(
        f"Moderator bot notification processor version {app.version} started successfully."
    )
