from .app import app, on_startup_finished_event, bot_publisher
from .utils import MockVideoStream, Config, CaptureLoop
from faststream import context
import asyncio


async def main():
    app_task = asyncio.create_task(app.run())
    try:
        await asyncio.wait_for(on_startup_finished_event.wait(), timeout=2)
    except asyncio.TimeoutError:
        print("App startup timed out")
        app_task.cancel()
        return

    if Config.DEBUG_MODE:
        mock_video = MockVideoStream(context.get("storage"))
        mock_video_task = asyncio.create_task(mock_video.start())
    else:
        mock_video = None
        mock_video_task = None

    capture_loop = CaptureLoop(
        context.get("storage"), context.get("logger"), bot_publisher
    )
    capture_task = asyncio.create_task(capture_loop.start())

    await app_task

    if mock_video_task and mock_video:
        mock_video_task.cancel()
        mock_video.process.terminate()
    capture_task.cancel()
    capture_loop.proc.terminate()


def run():
    asyncio.run(main())
