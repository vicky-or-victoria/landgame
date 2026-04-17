CREATE TABLE IF NOT EXISTS traditions (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    discord_id      BIGINT NOT NULL,
    tradition_id    TEXT NOT NULL,
    unlocked_at     TIMESTAMP DEFAULT NOW(),
    UNIQUE(guild_id, discord_id, tradition_id)
);
