CREATE TABLE IF NOT EXISTS research (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    discord_id      BIGINT NOT NULL,
    research_id     TEXT NOT NULL,
    unlocked_at     TIMESTAMP DEFAULT NOW(),
    UNIQUE(guild_id, discord_id, research_id)
);
