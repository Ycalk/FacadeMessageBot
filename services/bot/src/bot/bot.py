from aiomax import Bot
from .utils import (
    Config,
    RedisStateMachine,
    CityExtractor,
    CitiesClient,
    NameValidator,
    MemoryStateMachine,
)
import logging

# Attention: cities_client is None in testing mode
cities_client: CitiesClient
bot = Bot(Config.BOT_TOKEN, logging_level=logging.DEBUG)
if Config.IS_TESTING:
    state_machine = MemoryStateMachine()
    cities_client = None  # type: ignore
else:
    state_machine = RedisStateMachine()
    cities_client = CitiesClient(Config.CITIES_SERVICE_URL)

city_extractor = CityExtractor("src/bot/utils/city_extractor/cities.csv")
name_validator = NameValidator("src/bot/utils/name_validator/names.csv")
