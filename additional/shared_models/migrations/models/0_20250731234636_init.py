from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "max_id" INT NOT NULL UNIQUE,
    "username" VARCHAR(255) UNIQUE,
    "first_name" VARCHAR(255) NOT NULL,
    "last_name" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "message" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" VARCHAR(255) NOT NULL,
    "name" VARCHAR(255),
    "city" VARCHAR(255),
    "show_at" TIMESTAMPTZ,
    "state" VARCHAR(31) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "message"."state" IS 'PENDING_AUTO_MODERATION: pending_auto_moderation\nPENDING_MANUAL_MODERATION: pending_manual_moderation\nPENDING_MEDIA_FACADE_MODERATION: pending_media_facade_moderation\nREJECTED: rejected\nAPPROVED: approved\nCANCELED: canceled\nSHOWN: shown';
CREATE TABLE IF NOT EXISTS "media" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "url" VARCHAR(2048) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "message_id" INT NOT NULL UNIQUE REFERENCES "message" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "moderationlog" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "source" VARCHAR(12) NOT NULL,
    "result" VARCHAR(6) NOT NULL,
    "reason" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "message_id" INT NOT NULL REFERENCES "message" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "moderationlog"."source" IS 'AUTO: auto\nMANUAL: manual\nMEDIA_FACADE: media_facade';
COMMENT ON COLUMN "moderationlog"."result" IS 'REJECTED: auto\nAPPROVED: manual';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
