CREATE TABLE IF NOT EXISTS frontlines (
    id              SERIAL PRIMARY KEY,
    tile_coord      TEXT REFERENCES tiles(coord),
    attacker_id     BIGINT REFERENCES players(discord_id),
    defender_id     BIGINT REFERENCES players(discord_id),
    attacker_army   INTEGER REFERENCES armies(id),
    defender_army   INTEGER REFERENCES armies(id),
    started_at      TIMESTAMP DEFAULT NOW(),
    resolved        BOOLEAN DEFAULT FALSE
);
