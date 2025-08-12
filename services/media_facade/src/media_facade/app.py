from fastapi import FastAPI
from .utils import Config
from faststream.security import SASLPlaintext
from faststream.rabbit.fastapi import RabbitRouter
from importlib.metadata import version
from .handlers import webhooks_router

main_router = RabbitRouter(
    host=Config.RABBIT_HOST,
    port=Config.RABBIT_PORT,
    security=SASLPlaintext(
        username=Config.RABBIT_USER,
        password=Config.RABBIT_PASSWORD,
    ),
    include_in_schema=False,
)
app = FastAPI(title="Media Facade API", version=version("media_facade"))
app.include_router(main_router)
app.include_router(webhooks_router)
