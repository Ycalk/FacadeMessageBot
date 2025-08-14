from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "message" ALTER COLUMN "name" SET NOT NULL;
        ALTER TABLE "message" ALTER COLUMN "city" SET NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "message" ALTER COLUMN "name" DROP NOT NULL;
        ALTER TABLE "message" ALTER COLUMN "city" DROP NOT NULL;"""
