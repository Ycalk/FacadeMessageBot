from fastapi import FastAPI

from api.webhooks import router as webhooks_router
from api.maer_webhooks import router as maer_router
from ui.moderator_panel import init_ui


def create_webhook_app() -> FastAPI:
    """Создаёт FastAPI приложение для приёма webhooks."""
    app = FastAPI(title="Max Bot Webhooks")

    # Подключаем роутеры
    app.include_router(webhooks_router)  # /message/*
    app.include_router(maer_router)      # /maer/*

    # Подключаем NiceGUI для админ-панели
    init_ui(app)

    return app
