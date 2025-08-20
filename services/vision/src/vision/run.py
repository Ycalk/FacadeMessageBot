from .app import app, on_startup_finished_event, bot_publisher
from .utils import MockVideoStream, Config, CaptureLoop
from faststream import context
from redis.asyncio import Redis
from .utils import RedisStorage
import asyncio


async def main():
    app_task = asyncio.create_task(app.run())
    try:
        await asyncio.wait_for(on_startup_finished_event.wait(), timeout=2)
    except asyncio.TimeoutError:
        print("App startup timed out")
        app_task.cancel()
        return

    capture_loop = CaptureLoop(
        context.get("storage"), context.get("logger"), bot_publisher
    )
    capture_task = asyncio.create_task(capture_loop.start())

    await app_task

    capture_task.cancel()
    capture_loop.proc.terminate()


async def video_stream():
    if not Config.DEBUG_MODE:
        raise RuntimeError("Video stream is only available in debug mode")
    redis = Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DATA_STORAGE_DB,
    )
    mock_video = MockVideoStream(RedisStorage(redis))
    await mock_video.start()
    mock_video.process.terminate()


def run_mock_video_stream():
    asyncio.run(video_stream())


def run():
    asyncio.run(main())
