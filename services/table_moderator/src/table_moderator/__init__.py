import os
import sentry_sdk
if sentry := os.getenv("SENTRY_DSN"):
    sentry_sdk.init(dsn=sentry, send_default_pii=True)
from .run import run


__all__ = ["run"]
