from db.connection import get_pool
from config import DEV_MAX
import datetime

async def get_tile(bot, coord: str):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM tiles WHERE coord = $1", coord)
    return dict(row) if row else None

async def set_owner(bot, coord: str, discord_id: int):
    pool = await get_pool()
    await pool.execute(
        "UPDATE tiles SET owner_id = $1, last_action_at = $2 WHERE coord = $3",
        discord_id, datetime.datetime.utcnow(), coord
    )

async def adjust_dev(bot, coord: str, amount: int):
    pool = await get_pool()
    await pool.execute(
        "UPDATE tiles SET dev = LEAST(dev + $1, $2) WHERE coord = $3",
        amount, DEV_MAX, coord
    )

async def get_player_tiles(bot, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM tiles WHERE owner_id = $1", discord_id)
    return [dict(r) for r in rows]

async def get_all_tiles(bot):
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM tiles")
    return [dict(r) for r in rows]

async def apply_decay(bot, coord: str, amount: int):
    pool = await get_pool()
    await pool.execute(
        "UPDATE tiles SET dev = GREATEST(dev - $1, 0) WHERE coord = $2",
        amount, coord
    )

async def set_spawn(bot, coord: str, value: bool):
    pool = await get_pool()
    await pool.execute("UPDATE tiles SET is_spawn = $1 WHERE coord = $2", value, coord)

async def get_spawn_tiles(bot):
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM tiles WHERE is_spawn = TRUE AND owner_id IS NULL")
    return [dict(r) for r in rows]
