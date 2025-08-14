import httpx
from tortoise import Tortoise
from shared_models.database import get_tortoise_orm_config
from fastapi import FastAPI
from .utils import Config
from faststream.security import SASLPlaintext
from faststream.rabbit.fastapi import RabbitRouter
from importlib.metadata import version
from .handlers import webhooks_router, moderate_router
from faststream import context
from contextlib import asynccontextmanager

main_router = RabbitRouter(
    host=Config.RABBIT_HOST,
    port=Config.RABBIT_PORT,
    security=SASLPlaintext(
        username=Config.RABBIT_USER,
        password=Config.RABBIT_PASSWORD,
    ),
    include_in_schema=False,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    httpx_client = httpx.AsyncClient(
        base_url=Config.MEDIA_FACADE_API_BASE_URL
        if not Config.USE_MOCK
        else Config.MEDIA_FACADE_API_MOCK_BASE_URL,
        headers={"x-token": Config.MEDIA_FACADE_API_TOKEN},
    )
    httpx_mock_client = httpx.AsyncClient(
        base_url=Config.SELF_MOCK_URL,
        headers={"Authorization": f"Bearer {Config.SECRET_KEY}"},
    )
    app.state.httpx_client = httpx_client
    app.state.httpx_mock_client = httpx_mock_client
    context.set_global("httpx_client", httpx_client)
    await Tortoise.init(
        config=get_tortoise_orm_config(
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
            database=Config.POSTGRES_DB,
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
        )
    )
    await Tortoise.generate_schemas()

    yield

    await httpx_client.aclose()
    await httpx_mock_client.aclose()
    await Tortoise.close_connections()


app = FastAPI(
    title="Facade Message Bot API", version=version("media_facade"), lifespan=lifespan
)
main_router.include_router(moderate_router)
app.include_router(main_router)
app.include_router(webhooks_router)

if Config.USE_MOCK:
    from .handlers import mock_router

    app.include_router(mock_router)
