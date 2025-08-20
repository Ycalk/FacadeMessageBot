import asyncio
from .app import app, on_startup_finished_event
from shared_models.messaging import bot_exchange, bot_message_shown_queue
from .utils import MockVideoStream, Config, FrameMatcher, FrameProcessor
from faststream.log import logger
from faststream.rabbit import RabbitBroker
from redis.asyncio import Redis
from .utils import RedisStorage
from faststream.security import SASLPlaintext


async def app_runner():
    app_task = asyncio.create_task(app.run())
    try:
        await asyncio.wait_for(on_startup_finished_event.wait(), timeout=2)
    except asyncio.TimeoutError:
        print("App startup timed out")
        app_task.cancel()
        return

    await app_task


async def mock_video_stream_runner():
    if not Config.DEBUG_MODE:
        raise RuntimeError("Mock video stream is only available in debug mode")
    redis = Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DATA_STORAGE_DB,
    )
    mock_video = MockVideoStream(RedisStorage(redis))
    await mock_video.start()


async def frame_matcher_runner():
    redis = Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DATA_STORAGE_DB,
    )
    broker = RabbitBroker(
        host=Config.RABBIT_HOST,
        port=Config.RABBIT_PORT,
        security=SASLPlaintext(
            username=Config.RABBIT_USER,
            password=Config.RABBIT_PASSWORD,
        ),
    )
    await broker.start()
    frame_matcher = FrameMatcher(
        RedisStorage(redis),
        logger,
        broker.publisher(bot_message_shown_queue, bot_exchange),
    )
    try:
        await frame_matcher.start()
    finally:
        await broker.stop()


async def frame_processor_runner():
    redis = Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DATA_STORAGE_DB,
    )
    frame_processor = FrameProcessor(RedisStorage(redis), logger)
    await frame_processor.start()


def run_frame_matcher():
    asyncio.run(frame_matcher_runner())


def run_frame_processor():
    asyncio.run(frame_processor_runner())


def run_mock_video_stream():
    asyncio.run(mock_video_stream_runner())


def run_app():
    asyncio.run(app_runner())
