from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        case_sensitive=False,
    )

    # Development mode
    DEVELOP: bool = True

    # Max Bot
    BOT_TOKEN: str = ""
    BOT_WEBHOOK_URL: str = "https://maxbot.bnw-tech.ru"  # Базовый URL для вебхука бота
    BOT_WEBHOOK_SECRET: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Moder Service
    MODER_SERVICE_URL: str = "http://localhost:8001"

    # External moderator service (внешняя модерация)
    EXTERNAL_MODERATOR_URL: str = ""

    # Cities service
    CITIES_SERVICE_URL: str = "http://cities:8080"

    # Webhook server для приёма хуков от Moder Service
    WEBHOOK_HOST: str = "0.0.0.0"
    WEBHOOK_PORT: int = 8000

    # Name validation
    NAME_API_KEY: str = ""
    NAME_API_URL: str = (
        "https://api.nameapi.org/rest/v5.3/parser/personnameparser"
    )
    MINIMAL_NAME_CONFIDENCE: float = 0.6
    NAMES_FILE_PATH: str = "data/names.csv"

    # Bot settings
    MAX_MESSAGE_LENGTH: int = 80
    MAX_NAME_LENGTH: int = 15
    MAXIMUM_MESSAGES_PER_USER: int = 2
    MESSAGES_TIME_OUT_MINUTES: int = 1
    UNLIMITED_USERS: str = ""  # ID пользователей без лимитов (через запятую)

    # Антиспам
    ANTISPAM_MAX_ACTIONS: int = 5  # Макс. действий за окно
    ANTISPAM_WINDOW_SECONDS: int = 10  # Размер окна в секундах
    ANTISPAM_BLOCK_SECONDS: int = 30  # Блокировка при превышении лимита

    # Allowed characters for messages
    ALLOWED_CHARACTERS: str = (
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        "0123456789"
        " "
        "\n"
        "-—!@#$&()-=_;:'\",.?|\\`№"
    )

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://botuser:botpass@localhost:5432/botdb"
    )

    # Redis context TTL (7 дней в секундах)
    REDIS_CONTEXT_TTL: int = 7 * 24 * 3600  # 604800 секунд

    # Автомодерация
    AUTO_MODERATION_STUCK_TIMEOUT_MINUTES: int = 5  # Считать зависшим через 5 минут
    MISTRAL_API_KEY: str = ""  # Ключ Mistral AI для автомодерации
    MISTRAL_MODEL: str = "mistral-small-latest"  # Модель Mistral для модерации

    # Модераторы (список имён/ID для внутренней модерации)
    MODERATORS: str = "moderator_1, moderator_2"

    # VK модераторы (список имён/ID для VK модерации)
    VK_MODERATORS: str = "vk_moderator_1, vk_moderator_2, vk_moderator_3"

    # Пароли для админ-панелей
    ADMIN_INTERNAL_PASSWORD: str = "admin"
    ADMIN_VK_PASSWORD: str = "vkadmin"

    # Токен для авторизации входящих запросов к API
    API_TOKEN: str = ""

    # Ссылка на условия пользования (отображается на стартовом экране)
    TERMS_OF_USE_URL: str = ""

    # Абсолютный путь к папке data с фонами и генерируемыми превью
    DATA_DIR: str = "/home/app/data"

    # Maer API (внешняя модерация)
    MAER_API_URL: str = ""
    MAER_API_TOKEN: str = ""

    @property
    def unlimited_users_list(self) -> list[int]:
        """Возвращает список ID пользователей без лимитов."""
        return [int(u.strip()) for u in self.UNLIMITED_USERS.split(",") if u.strip()]

    @property
    def moderators_list(self) -> list[str]:
        """Возвращает список модераторов."""
        return [m.strip() for m in self.MODERATORS.split(",") if m.strip()]

    @property
    def vk_moderators_list(self) -> list[str]:
        """Возвращает список VK модераторов."""
        return [m.strip() for m in self.VK_MODERATORS.split(",") if m.strip()]


Config = Settings()
