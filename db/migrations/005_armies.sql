CREATE TABLE IF NOT EXISTS armies (
    id          SERIAL PRIMARY KEY,
    owner_id    BIGINT REFERENCES players(discord_id) ON DELETE CASCADE,
    name        TEXT,
    location    TEXT REFERENCES tiles(coord),
    created_at  TIMESTAMP DEFAULT NOW()
);
