-- Stores per-guild bot configuration (channels, roles, menu message id, etc.)
CREATE TABLE IF NOT EXISTS guild_config (
    guild_id        BIGINT NOT NULL,
    key             TEXT NOT NULL,
    value           TEXT,
    PRIMARY KEY (guild_id, key)
);

-- Tracks the registration embed message per guild
CREATE TABLE IF NOT EXISTS registration_message (
    guild_id        BIGINT PRIMARY KEY,
    channel_id      BIGINT NOT NULL,
    message_id      BIGINT NOT NULL,
    player_role_id  BIGINT
);
