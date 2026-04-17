CREATE TABLE IF NOT EXISTS buildings (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    tile_coord      TEXT NOT NULL,
    name            TEXT NOT NULL,
    category        TEXT NOT NULL,
    tier            INTEGER DEFAULT 1,
    built_at        TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS buildings_guild_coord ON buildings(guild_id, tile_coord);
