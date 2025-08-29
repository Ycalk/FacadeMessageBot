import asyncio
import logging
from bot.bot import bot
from maxapi.types.input_media import InputMedia
from maxapi.enums.upload_type import UploadType


async def main():
    bot.logger.level = logging.ERROR
    print(
        await bot.get_upload_url(UploadType.IMAGE)
    )


def get_upload_image_token():
    asyncio.run(main())
