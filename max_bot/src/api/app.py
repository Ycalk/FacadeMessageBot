from importlib import import_module

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from maxapi.exceptions.max import MaxApiError
from nicegui import ui

from api.webhooks import router as webhooks_router
from api.maer_webhooks import router as maer_router
from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Создаёт FastAPI приложение."""
    app = FastAPI(
        title="Max Bot Webhooks",
        docs_url="/docs" if Config.DEVELOP else None,
        redoc_url="/redoc" if Config.DEVELOP else None,
        openapi_url="/openapi.json" if Config.DEVELOP else None,
    )

    @app.exception_handler(MaxApiError)
    async def max_api_error_handler(request: Request, exc: MaxApiError) -> JSONResponse:
        if exc.code == 404 and isinstance(exc.raw, dict) and exc.raw.get("code") == "chat.not.found":
            logger.warning(f"Чат не найден (удалён или недоступен): {exc.raw.get('message')}")
            sentry_sdk.capture_message(
                f"Чат не найден: {exc.raw.get('message')}",
                level="warning",
            )
            return JSONResponse(status_code=200, content={"ok": True})
        logger.error(f"Ошибка MAX API [{exc.code}]: {exc.raw}")
        sentry_sdk.capture_exception(exc)
        return JSONResponse(status_code=200, content={"ok": True})

    # Подключаем роутеры
    app.include_router(webhooks_router)  # /message/*
    app.include_router(maer_router)      # /maer/*

    # Регистрируем админ-панели (импорт активирует @ui.page декораторы)
    import_module("ui.moderator_panel")  # /admin_internal
    import_module("ui.admin_vk")         # /admin_vk

    if not Config.UI_STORAGE_SECRET:
        raise RuntimeError("UI_STORAGE_SECRET не задан")

    # Подключаем NiceGUI для админ-панелей
    ui.run_with(
        app,
        mount_path='/ui',
        storage_secret=Config.UI_STORAGE_SECRET,
    )

    return app
