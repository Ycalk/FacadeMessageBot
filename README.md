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
# Сгенерировать внутренние TLS-сертификаты
./certs/generate.sh --force

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
POSTGRES_SSL=true
POSTGRES_CA_CERT=/certs/ca/ca.crt
REDIS_HOST=localhost
REDIS_PASSWORD=...
REDIS_SSL=true
REDIS_CA_CERT=/certs/ca/ca.crt

# Elasticsearch (cities service)
ELASTIC_PASSWORD=...
CITIES_API_TOKEN=...
CITIES_SERVICE_URL=https://cities:8080
CITIES_VERIFY_TLS=true
CITIES_CA_CERT=/certs/ca/ca.crt

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

# Учетки admin-панелей (формат: user1:pass1,user2:pass2)
ADMIN_INTERNAL_CREDENTIALS=admin:...
ADMIN_VK_CREDENTIALS=vkadmin:...
SMARTCAPTCHA_CLIENT_KEY=ysc1_...
SMARTCAPTCHA_SERVER_KEY=ysc2_...

# Режим разработки (отключает запросы к Maer)
DEVELOP=false
```

## Admin-панели

Доступны по адресу сервера после авторизации по логину и паролю.

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
