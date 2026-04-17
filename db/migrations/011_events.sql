CREATE TABLE IF NOT EXISTS events_log (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    turn            INTEGER,
    event_type      TEXT NOT NULL,
    target          TEXT,
    description     TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS events_guild ON events_log(guild_id);

CREATE TABLE IF NOT EXISTS game_state (
    guild_id        BIGINT NOT NULL,
    key             TEXT NOT NULL,
    value           TEXT,
    PRIMARY KEY (guild_id, key)
);
