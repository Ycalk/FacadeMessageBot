from aiomax import Bot
from .utils import Config, StateMachine
import logging


bot = Bot(Config.BOT_TOKEN, logging_level=logging.DEBUG)
state_machine = StateMachine()
