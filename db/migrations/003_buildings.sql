CREATE TABLE IF NOT EXISTS buildings (
    id          SERIAL PRIMARY KEY,
    tile_coord  TEXT REFERENCES tiles(coord) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    tier        INTEGER DEFAULT 1,
    built_at    TIMESTAMP DEFAULT NOW()
);
