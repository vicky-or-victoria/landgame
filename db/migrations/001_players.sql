CREATE TABLE IF NOT EXISTS players (
    discord_id      BIGINT PRIMARY KEY,
    name            TEXT NOT NULL,
    gold            INTEGER DEFAULT 300,
    food            INTEGER DEFAULT 200,
    materials       INTEGER DEFAULT 200,
    influence       INTEGER DEFAULT 0,
    prestige        INTEGER DEFAULT 0,
    grace_until     TIMESTAMP,
    registered_at   TIMESTAMP DEFAULT NOW()
);
