from aiomax import Bot
from .utils import Config, StateMachine, CityExtractor, NameValidator
import logging


bot = Bot(Config.BOT_TOKEN, logging_level=logging.DEBUG)
state_machine = StateMachine()
city_extractor = CityExtractor("src/bot/utils/city_extractor/cities.csv")
name_validator = NameValidator("src/bot/utils/name_validator/names.csv")
