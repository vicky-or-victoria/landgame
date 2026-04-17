CREATE TABLE IF NOT EXISTS research (
    id          SERIAL PRIMARY KEY,
    player_id   BIGINT REFERENCES players(discord_id) ON DELETE CASCADE,
    research_id TEXT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(player_id, research_id)
);
