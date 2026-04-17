CREATE TABLE IF NOT EXISTS frontlines (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    tile_coord      TEXT,
    attacker_id     BIGINT,
    defender_id     BIGINT,
    attacker_army   INTEGER,
    defender_army   INTEGER,
    started_at      TIMESTAMP DEFAULT NOW(),
    resolved        BOOLEAN DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS frontlines_guild ON frontlines(guild_id, tile_coord);
