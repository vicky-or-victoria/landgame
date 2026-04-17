CREATE TABLE IF NOT EXISTS market_orders (
    id          SERIAL PRIMARY KEY,
    player_id   BIGINT REFERENCES players(discord_id) ON DELETE CASCADE,
    resource    TEXT NOT NULL,
    amount      INTEGER NOT NULL,
    price       INTEGER NOT NULL,
    order_type  TEXT NOT NULL,
    filled      BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS market_prices (
    resource    TEXT PRIMARY KEY,
    price       INTEGER NOT NULL,
    updated_at  TIMESTAMP DEFAULT NOW()
);

INSERT INTO market_prices (resource, price) VALUES
    ('gold', 1),
    ('food', 2),
    ('materials', 3)
ON CONFLICT DO NOTHING;
