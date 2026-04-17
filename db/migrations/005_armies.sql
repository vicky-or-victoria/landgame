CREATE TABLE IF NOT EXISTS armies (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    owner_id        BIGINT NOT NULL,
    name            TEXT,
    location        TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS armies_guild_owner ON armies(guild_id, owner_id);
