from aiomax import Bot
from .utils import Config
import logging

bot = Bot(Config.BOT_TOKEN, logging_level=logging.DEBUG)
