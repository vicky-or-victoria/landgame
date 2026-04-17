CREATE TABLE IF NOT EXISTS treaties (
    id              SERIAL PRIMARY KEY,
    player_a        BIGINT REFERENCES players(discord_id),
    player_b        BIGINT REFERENCES players(discord_id),
    treaty_type     TEXT NOT NULL,
    status          TEXT DEFAULT 'pending',
    offered_at      TIMESTAMP DEFAULT NOW(),
    resolved_at     TIMESTAMP,
    expires_at      TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wars (
    id              SERIAL PRIMARY KEY,
    attacker_id     BIGINT REFERENCES players(discord_id),
    defender_id     BIGINT REFERENCES players(discord_id),
    declared_at     TIMESTAMP DEFAULT NOW(),
    hostilities_at  TIMESTAMP,
    ended_at        TIMESTAMP,
    active          BOOLEAN DEFAULT TRUE
);
