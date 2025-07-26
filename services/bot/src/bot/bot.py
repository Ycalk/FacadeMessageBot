from aiomax import Bot
from .utils import Config, StateMachine, CityExtractor
import logging


bot = Bot(Config.BOT_TOKEN, logging_level=logging.DEBUG)
state_machine = StateMachine()
city_extractor = CityExtractor("src/bot/utils/city_extractor/cities.csv")
