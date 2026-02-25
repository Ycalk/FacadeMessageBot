# MAX Facade Message Bot

Бот для мессенджера MAX — позволяет пользователям отправить текстовое поздравление на медиафасад здания. Сообщения проходят многоуровневую модерацию (AI + ручная), после чего отображаются на фасаде, а желающие получают фото своего поздравления.

## Как работает

### Диалог с пользователем

1. **Текст** — до 80 символов, проверяется whitelist символов + разрешённые эмодзи
2. **Имя** — белый список `names.csv` + внешний API валидации
3. **Город** — fuzzy-поиск через Elasticsearch
4. **Фон** — выбор из нескольких вариантов подложки
5. Бот генерирует превью и отправляет на модерацию

### Пайплайн модерации

```
created
  └→ auto_moderation       # Mistral AI + чёрный список
       ├→ rejected
       └→ internal_moderation  # Голосование внутренних модераторов
            ├→ rejected
            └→ vk_moderation   # Голосование VK модераторов
                 ├→ rejected
                 └→ maer_moderation  # Внешний Maer API
                      ├→ rejected
                      └→ approved
```

После одобрения: vision серврис шлёт вебхук с фото → бот отправляет фото пользователю (если он хотел).

## Технологии

| Слой | Технология |
|------|------------|
| Бот | Python 3.11+, maxapi (MAX messenger SDK) |
| Web | FastAPI + NiceGUI (admin UI) |
| БД | PostgreSQL (сообщения), Redis (FSM состояния) |
| Поиск | Elasticsearch (города, `cities/`) |
| AI | Mistral AI (автоматическая пре-модерация) |
| Изображения | Pillow (генерация превью) |

## Запуск

```bash
# Все сервисы
docker-compose up --build

# Только инфраструктура (локальная разработка)
docker-compose up postgres redis elasticsearch cities

# Бот локально
pip install -e ./max_bot
python max_bot/src/main.py
```

Нужен `.env` файл. БД создаётся автоматически при старте.

## Конфигурация (`.env`)

```env
# Бот
BOT_TOKEN=...
BOT_WEBHOOK_URL=https://...

# БД
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/botdb
REDIS_HOST=localhost

# Модерация
MISTRAL_API_KEY=...
MAER_API_URL=https://...
MAER_API_TOKEN=...

# Валидация имён
NAME_API_KEY=...
NAME_API_URL=https://...

# Лимиты (дефолты)
MAX_MESSAGE_LENGTH=80
MAX_NAME_LENGTH=15
MAXIMUM_MESSAGES_PER_USER=2

# Пароли admin-панелей
ADMIN_INTERNAL_PASSWORD=...
ADMIN_VK_PASSWORD=...

# Режим разработки (отключает запросы к Maer)
DEVELOP=false
```

## Admin-панели

Доступны по адресу сервера после авторизации по паролю.

### `/admin_internal` — Внутренняя модерация
- Таблица всех сообщений со статусами
- Голосование модераторов (чекбоксы по каждому)
- Автоодобрение по модераторам (toggle)
- Чёрный список слов (добавление вручную / импорт .txt)
- Редактор промпта Mistral
- Рассылка напоминаний

### `/admin_vk` — VK модерация
- Сообщения на стадии VK и выше
- Голосование VK-модераторов

Оба блока содержат блок статистики: всего сообщений, пользователей, ждут фото, фото отправлено + разбивка по статусам.

## Webhooks

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/message/approved` | Список одобренных сообщений (для фасада) |
| POST | `/message/shown` | Фасад показал сообщение → скачать фото и отправить пользователю |
| POST | `/maer/moderated` | Результат модерации от Maer API |
| POST | `/maer/shown` | Сообщение показано на Maer-фасаде |

Все входящие вебхуки защищены Bearer-токеном (`API_TOKEN`).

## Структура проекта

```
max_bot/src/
├── main.py                # Точка входа
├── core/                  # Config, logger, emoji_whitelist
├── db/                    # SQLAlchemy модели и сессия
├── bot/
│   ├── routers/           # system, text, callbacks
│   └── handlers/          # Один файл на шаг FSM
├── api/
│   ├── webhooks.py        # /message/*
│   └── maer_webhooks.py   # /maer/*
├── services/              # Вся бизнес-логика
└── ui/                    # NiceGUI admin-панели

cities/                    # Микросервис поиска городов
data/                      # Фоны, шрифты, эмодзи, CSV городов
```
