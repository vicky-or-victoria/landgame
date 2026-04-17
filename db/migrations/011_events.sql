CREATE TABLE IF NOT EXISTS events_log (
    id          SERIAL PRIMARY KEY,
    turn        INTEGER,
    event_type  TEXT NOT NULL,
    target      TEXT,
    description TEXT,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS game_state (
    key     TEXT PRIMARY KEY,
    value   TEXT
);

INSERT INTO game_state (key, value) VALUES
    ('turn', '1'),
    ('paused', 'false'),
    ('turn_interval_hours', '24')
ON CONFLICT DO NOTHING;
