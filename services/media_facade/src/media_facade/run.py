import uvicorn
from .utils import Config


def run():
    uvicorn.run("media_facade:app", host="0.0.0.0", port=Config.PORT)
