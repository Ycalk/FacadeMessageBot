from .app import app
import asyncio


async def main():
    await app.run()


def run():
    asyncio.run(main())
