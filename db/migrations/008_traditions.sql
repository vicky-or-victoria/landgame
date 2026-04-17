CREATE TABLE IF NOT EXISTS traditions (
    id              SERIAL PRIMARY KEY,
    player_id       BIGINT REFERENCES players(discord_id) ON DELETE CASCADE,
    tradition_id    TEXT NOT NULL,
    unlocked_at     TIMESTAMP DEFAULT NOW(),
    UNIQUE(player_id, tradition_id)
);
