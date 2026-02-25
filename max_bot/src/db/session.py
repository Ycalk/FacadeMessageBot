from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import Config

engine = create_async_engine(
    Config.DATABASE_URL,
    pool_size=30,
    max_overflow=20,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)
