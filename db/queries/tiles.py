from db.connection import get_pool
from config import DEV_MAX
import datetime


async def get_tile(bot, guild_id: int, coord: str):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM tiles WHERE guild_id = $1 AND coord = $2",
        guild_id, coord
    )
    return dict(row) if row else None


async def set_owner(bot, guild_id: int, coord: str, discord_id: int):
    pool = await get_pool()
    await pool.execute(
        "UPDATE tiles SET owner_id = $1, last_action_at = $2 WHERE guild_id = $3 AND coord = $4",
        discord_id, datetime.datetime.utcnow(), guild_id, coord
    )


async def adjust_dev(bot, guild_id: int, coord: str, amount: int):
    pool = await get_pool()
    await pool.execute(
        "UPDATE tiles SET dev = LEAST(dev + $1, $2) WHERE guild_id = $3 AND coord = $4",
        amount, DEV_MAX, guild_id, coord
    )


async def get_player_tiles(bot, guild_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM tiles WHERE guild_id = $1 AND owner_id = $2",
        guild_id, discord_id
    )
    return [dict(r) for r in rows]


async def get_all_tiles(bot, guild_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM tiles WHERE guild_id = $1",
        guild_id
    )
    return [dict(r) for r in rows]


async def apply_decay(bot, guild_id: int, coord: str, amount: int):
    pool = await get_pool()
    await pool.execute(
        "UPDATE tiles SET dev = GREATEST(dev - $1, 0) WHERE guild_id = $2 AND coord = $3",
        amount, guild_id, coord
    )


async def set_spawn(bot, guild_id: int, coord: str, value: bool):
    pool = await get_pool()
    await pool.execute(
        "UPDATE tiles SET is_spawn = $1 WHERE guild_id = $2 AND coord = $3",
        value, guild_id, coord
    )


async def get_spawn_tiles(bot, guild_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM tiles WHERE guild_id = $1 AND is_spawn = TRUE AND owner_id IS NULL",
        guild_id
    )
    return [dict(r) for r in rows]


async def ensure_guild_map(guild_id: int):
    """Insert a blank 64×64 grid for a guild if it doesn't exist yet."""
    pool = await get_pool()
    existing = await pool.fetchval(
        "SELECT COUNT(*) FROM tiles WHERE guild_id = $1", guild_id
    )
    if existing and existing > 0:
        return  # Already seeded

    records = []
    for row in range(64):
        for col in range(64):
            coord = f"{chr(65 + col)}{row + 1}"
            records.append((guild_id, coord))

    await pool.executemany(
        "INSERT INTO tiles (guild_id, coord, terrain) VALUES ($1, $2, 'flat') ON CONFLICT DO NOTHING",
        records
    )
