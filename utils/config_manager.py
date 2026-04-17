"""
Guild-aware config manager backed by the guild_config table.
Each Discord server gets its own isolated configuration.
"""
import json
import os
from db.connection import get_pool

CHANNEL_KEYS = [
    "world_map", "world_events", "turn_log", "menu",
    "commands", "battle_reports", "leaderboard", "public_log", "gm_alerts",
]

# Fallback in-memory defaults (used before DB is ready)
_cache: dict[int, dict] = {}


async def _db_get(guild_id: int, key: str):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT value FROM guild_config WHERE guild_id = $1 AND key = $2",
        guild_id, key
    )
    return row["value"] if row else None


async def _db_set(guild_id: int, key: str, value):
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO guild_config (guild_id, key, value)
           VALUES ($1, $2, $3)
           ON CONFLICT (guild_id, key) DO UPDATE SET value = EXCLUDED.value""",
        guild_id, key, str(value) if value is not None else None
    )


class GuildConfig:
    """Async, per-guild config accessor."""

    def __init__(self, guild_id: int):
        self.guild_id = guild_id

    async def get_channel(self, name: str):
        val = await _db_get(self.guild_id, f"channel_{name}")
        return int(val) if val else None

    async def set_channel(self, name: str, channel_id: int):
        await _db_set(self.guild_id, f"channel_{name}", channel_id)

    async def get_gm_role(self):
        val = await _db_get(self.guild_id, "gm_role")
        return int(val) if val else None

    async def set_gm_role(self, role_id: int):
        await _db_set(self.guild_id, "gm_role", role_id)

    async def get_player_role(self):
        val = await _db_get(self.guild_id, "player_role")
        return int(val) if val else None

    async def set_player_role(self, role_id: int):
        await _db_set(self.guild_id, "player_role", role_id)

    async def get_menu_message(self):
        val = await _db_get(self.guild_id, "menu_message")
        return int(val) if val else None

    async def set_menu_message(self, message_id: int):
        await _db_set(self.guild_id, "menu_message", message_id)

    async def get_registration_message(self):
        pool = await get_pool()
        row = await pool.fetchrow(
            "SELECT channel_id, message_id, player_role_id FROM registration_message WHERE guild_id = $1",
            self.guild_id
        )
        return dict(row) if row else None

    async def set_registration_message(self, channel_id: int, message_id: int, player_role_id=None):
        pool = await get_pool()
        await pool.execute(
            """INSERT INTO registration_message (guild_id, channel_id, message_id, player_role_id)
               VALUES ($1, $2, $3, $4)
               ON CONFLICT (guild_id) DO UPDATE
               SET channel_id = EXCLUDED.channel_id,
                   message_id = EXCLUDED.message_id,
                   player_role_id = EXCLUDED.player_role_id""",
            self.guild_id, channel_id, message_id, player_role_id
        )

    async def is_setup_complete(self):
        val = await _db_get(self.guild_id, "setup_complete")
        return val == "true"

    async def mark_setup_complete(self):
        await _db_set(self.guild_id, "setup_complete", "true")

    async def get_missing_channels(self):
        missing = []
        for name in CHANNEL_KEYS:
            val = await _db_get(self.guild_id, f"channel_{name}")
            if not val:
                missing.append(name)
        return missing


class ConfigManager:
    """Bot-level config manager: returns per-guild GuildConfig objects."""

    def for_guild(self, guild_id: int) -> GuildConfig:
        return GuildConfig(guild_id)

    # Legacy shim helpers so old code calling bot.config.get_channel() still
    # raises a clear error instead of silently doing the wrong thing.
    def get_channel(self, *a, **kw):
        raise RuntimeError("Use bot.guild_config(guild_id).get_channel() instead.")

    def set_channel(self, *a, **kw):
        raise RuntimeError("Use bot.guild_config(guild_id).set_channel() instead.")
