CREATE TABLE IF NOT EXISTS treaties (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    player_a        BIGINT,
    player_b        BIGINT,
    treaty_type     TEXT NOT NULL,
    status          TEXT DEFAULT 'pending',
    offered_at      TIMESTAMP DEFAULT NOW(),
    resolved_at     TIMESTAMP,
    expires_at      TIMESTAMP
);
CREATE INDEX IF NOT EXISTS treaties_guild ON treaties(guild_id);

CREATE TABLE IF NOT EXISTS wars (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    attacker_id     BIGINT,
    defender_id     BIGINT,
    declared_at     TIMESTAMP DEFAULT NOW(),
    hostilities_at  TIMESTAMP,
    ended_at        TIMESTAMP,
    active          BOOLEAN DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS wars_guild ON wars(guild_id);
