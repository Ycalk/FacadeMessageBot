from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "message" ADD "show_time_end" TIMESTAMPTZ;
        ALTER TABLE "message" ADD "show_time_start" TIMESTAMPTZ;
        ALTER TABLE "message" DROP COLUMN "show_at";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "message" ADD "show_at" TIMESTAMPTZ;
        ALTER TABLE "message" DROP COLUMN "show_time_end";
        ALTER TABLE "message" DROP COLUMN "show_time_start";"""
