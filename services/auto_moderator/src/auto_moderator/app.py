from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream import Context, ContextRepo
from faststream.security import SASLPlaintext
from importlib.metadata import version
from mistralai import Mistral
from logging import Logger
from auto_moderator.handlers import moderate_router, add_to_black_list_router
from .utils import Config, BlackList


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
    title="Auto Moderator",
    version=version("auto_moderator"),
    description="A service for moderating messages in Facade Message Bot",
)
broker.include_router(moderate_router)
broker.include_router(add_to_black_list_router)


@app.on_startup
async def on_startup(context: ContextRepo):
    context.set_global("mistral", Mistral(Config.MISTRAL_API_KEY))
    black_list = BlackList()
    await black_list.init()
    context.set_global("black_list", black_list)


@app.after_startup
async def after_startup(logger: Logger = Context()):
    logger.info(f"Auto Moderator version {app.version} started successfully.")
