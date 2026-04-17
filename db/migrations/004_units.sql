CREATE TABLE IF NOT EXISTS units (
    id              SERIAL PRIMARY KEY,
    guild_id        BIGINT NOT NULL,
    owner_id        BIGINT NOT NULL,
    unit_type       TEXT NOT NULL,
    size            INTEGER DEFAULT 0,
    is_levy         BOOLEAN DEFAULT TRUE,
    home_tile       TEXT,
    current_tile    TEXT,
    army_id         INTEGER
);
CREATE INDEX IF NOT EXISTS units_guild_owner ON units(guild_id, owner_id);
