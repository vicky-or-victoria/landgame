CREATE TABLE IF NOT EXISTS tiles (
    coord           TEXT PRIMARY KEY,
    name            TEXT,
    terrain         TEXT NOT NULL,
    dev             INTEGER DEFAULT 0,
    owner_id        BIGINT REFERENCES players(discord_id) ON DELETE SET NULL,
    captured_at     TIMESTAMP,
    stabilized      BOOLEAN DEFAULT TRUE,
    is_spawn        BOOLEAN DEFAULT FALSE,
    last_action_at  TIMESTAMP
);
