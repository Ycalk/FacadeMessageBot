from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "moderationlog" ALTER COLUMN "result" TYPE VARCHAR(8) USING "result"::VARCHAR(8);
        COMMENT ON COLUMN "moderationlog"."result" IS 'REJECTED: rejected
APPROVED: approved';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        COMMENT ON COLUMN "moderationlog"."result" IS 'REJECTED: auto
APPROVED: manual';
        ALTER TABLE "moderationlog" ALTER COLUMN "result" TYPE VARCHAR(6) USING "result"::VARCHAR(6);"""
