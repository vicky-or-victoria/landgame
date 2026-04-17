CREATE TABLE IF NOT EXISTS market_orders (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    owner_id        BIGINT NOT NULL,
    resource        TEXT NOT NULL,
    amount          INTEGER NOT NULL,
    price           INTEGER NOT NULL,
    order_type      TEXT NOT NULL,
    filled          BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS market_guild ON market_orders(guild_id);

CREATE TABLE IF NOT EXISTS market_prices (
    guild_id        BIGINT NOT NULL,
    resource        TEXT NOT NULL,
    price           INTEGER NOT NULL,
    updated_at      TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (guild_id, resource)
);
