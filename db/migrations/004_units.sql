CREATE TABLE IF NOT EXISTS units (
    id              SERIAL PRIMARY KEY,
    owner_id        BIGINT REFERENCES players(discord_id) ON DELETE CASCADE,
    home_tile       TEXT REFERENCES tiles(coord),
    unit_type       TEXT NOT NULL,
    size            INTEGER DEFAULT 0,
    is_levy         BOOLEAN DEFAULT TRUE,
    current_tile    TEXT REFERENCES tiles(coord),
    army_id         INTEGER
);
