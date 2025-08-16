from redis.asyncio import Redis
from flashtext import KeywordProcessor
from .config import Config


class BlackList:
    def __init__(self) -> None:
        self.redis = Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_BLACK_LIST_STORAGE_DB,
        )
        self.keyword_processor = KeywordProcessor()

    async def init(self) -> None:
        """Initialize the keyword processor with blacklisted words from Redis."""
        black_list = await self.redis.smembers("black_list")  # type: ignore
        self.keyword_processor.add_keywords_from_list(
            [word.decode("utf-8") for word in black_list]
        )

    def is_blacklisted(self, text: str) -> bool:
        """Check if the text contains any blacklisted words."""
        return bool(self.keyword_processor.extract_keywords(text))

    async def add_to_blacklist(self, word: str) -> None:
        """Add a word to the blacklist."""
        await self.redis.sadd("black_list", word)  # type: ignore
        self.keyword_processor.add_keyword(word)

    async def close(self) -> None:
        """Close Redis connection."""
        await self.redis.close()
