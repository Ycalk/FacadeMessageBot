import os
import sentry_sdk
if sentry := os.getenv("SENTRY_DSN"):
    sentry_sdk.init(dsn=sentry, send_default_pii=True, environment=os.getenv("SENTRY_ENV"))
from .run import run_frame_matcher, run_mock_video_stream, run_frame_processor, run_app

__all__ = [
    "run_frame_matcher",
    "run_mock_video_stream",
    "run_frame_processor",
    "run_app",
]
