from aiomax import Bot
from .utils import (
    Config,
    RedisStateMachine,
    CityExtractor,
    NameValidator,
    MemoryStateMachine,
)
import logging


bot = Bot(Config.BOT_TOKEN, logging_level=logging.INFO)
if Config.IS_TESTING:
    state_machine = MemoryStateMachine()
else:
    state_machine = RedisStateMachine()

city_extractor = CityExtractor("src/bot/utils/city_extractor/cities.csv")
name_validator = NameValidator("src/bot/utils/name_validator/names.csv")
