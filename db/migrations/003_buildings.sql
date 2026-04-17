CREATE TABLE IF NOT EXISTS buildings (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    coord           TEXT NOT NULL,
    owner_id        BIGINT NOT NULL,
    building_type   TEXT NOT NULL,
    tier            INTEGER DEFAULT 1,
    built_at        TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS buildings_guild_coord ON buildings(guild_id, coord);
