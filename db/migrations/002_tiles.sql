-- Per-guild tile map (64×64, pre-seeded per guild)
CREATE TABLE IF NOT EXISTS tiles (
    guild_id        BIGINT NOT NULL,
    coord           TEXT NOT NULL,
    name            TEXT,
    terrain         TEXT NOT NULL DEFAULT 'flat',
    dev             INTEGER DEFAULT 0,
    owner_id        BIGINT,
    captured_at     TIMESTAMP,
    stabilized      BOOLEAN DEFAULT TRUE,
    is_spawn        BOOLEAN DEFAULT FALSE,
    last_action_at  TIMESTAMP,
    PRIMARY KEY (guild_id, coord)
);
