import os
import sentry_sdk
if sentry := os.getenv("SENTRY_DSN"):
    sentry_sdk.init(dsn=sentry, send_default_pii=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from es_client import get_elasticsearch_client, INDEX_NAME, INDEX_MAPPING
from routes import router
from utils import parse_csv_cities


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при запуске и очистка при завершении"""
    try:
        es = get_elasticsearch_client()
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(
                index=INDEX_NAME,
                settings=INDEX_MAPPING["settings"],
                mappings=INDEX_MAPPING["mappings"]
            )
            # Загружаем города из файла при первом запуске
            result = parse_csv_cities(settings.cities_file_path, es, INDEX_NAME)
            if result["success"]:
                print(f"Loaded {result['cities_loaded']} cities on startup")
            else:
                print(f"Failed to load cities: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"Startup error: {e}")

    yield

app = FastAPI(
    lifespan=lifespan,
    title="Cities Search API",
    description="""
    ## API для поиска российских городов 🇷🇺

    Этот API предоставляет возможности для работы с базой данных российских городов:

    * **Поиск городов** - нечёткий поиск по названию на русском языке
    * **Добавление городов** - создание новых записей в базе
    * **Получение информации** - простая информация о конкретном городе
    * **Мониторинг** - проверка состояния сервиса и подключений

    ### Технологии
    - **FastAPI** - современный веб-фреймворк
    - **Elasticsearch** - полнотекстовый поиск с поддержкой русского языка
    - **Pydantic** - валидация данных

    ### Особенности поиска
    - Русский анализатор с стеммингом
    - Поддержка опечаток (fuzziness)
    - Приоритет точных совпадений
    - Сортировка по релевантности
    """,
    version="1.0.0",
    contact={
        "name": "Support",
        "email": "fmannanov01@gmail.com"
    },
    root_path="/cities",
    openapi_tags=[
        {
            "name": "cities",
            "description": "**Операции с российскими городами**: поиск, создание, получение информации. "
                         "Все операции работают с индексом Elasticsearch и поддерживают валидацию данных.",
        },
        {
            "name": "health",
            "description": "**Мониторинг сервиса**: проверка состояния приложения и подключения к Elasticsearch. "
                         "Используется для проверок работоспособности в production.",
        },
    ],
    servers=[
        {
            "url": "http://localhost/cities",
            "description": "Development server via nginx"
        },
        {
            "url": "http://localhost:8081/cities",
            "description": "Direct development server"
        }
    ]
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(router)
