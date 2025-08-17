import asyncio
import logging
from bot.bot import bot
from aiomax.types import InputFile, UploadType


async def main():
    bot.logger.level = logging.ERROR
    print(
        await bot.upload(InputFile.from_file("image.png", upload_type=UploadType.IMAGE))
    )


def get_upload_image_token():
    asyncio.run(main())
