-- Per-guild player registry
CREATE TABLE IF NOT EXISTS players (
    guild_id        BIGINT NOT NULL,
    discord_id      BIGINT NOT NULL,
    name            TEXT NOT NULL,
    gold            INTEGER DEFAULT 300,
    food            INTEGER DEFAULT 200,
    materials       INTEGER DEFAULT 200,
    influence       INTEGER DEFAULT 0,
    prestige        INTEGER DEFAULT 0,
    grace_until     TIMESTAMP,
    registered_at   TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (guild_id, discord_id)
);
