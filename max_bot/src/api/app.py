from importlib import import_module

from fastapi import FastAPI
from nicegui import ui

from api.webhooks import router as webhooks_router
from api.maer_webhooks import router as maer_router


def create_webhook_app() -> FastAPI:
    """Создаёт FastAPI приложение для приёма webhooks."""
    app = FastAPI(title="Max Bot Webhooks")

    # Подключаем роутеры
    app.include_router(webhooks_router)  # /message/*
    app.include_router(maer_router)      # /maer/*

    # Регистрируем админ-панели (импорт активирует @ui.page декораторы)
    import_module("ui.moderator_panel")  # /admin_internal
    import_module("ui.admin_vk")         # /admin_vk

    # Подключаем NiceGUI для админ-панелей
    ui.run_with(
        app,
        mount_path='/ui',
        storage_secret='secret_key_for_ui',
    )

    return app
