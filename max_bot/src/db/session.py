import ssl

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import Config

connect_args = {}
if Config.POSTGRES_SSL:
    ssl_context = ssl.create_default_context(cafile=Config.POSTGRES_CA_CERT)
    connect_args["ssl"] = ssl_context

engine = create_async_engine(
    Config.DATABASE_URL,
    pool_size=30,
    max_overflow=20,
    connect_args=connect_args,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)
