from db.connection import get_pool
from config import START_GOLD, START_FOOD, START_MATERIALS, START_INFLUENCE
import datetime

async def get_player(bot, discord_id: int):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM players WHERE discord_id = $1", discord_id)
    if not row:
        return None
    tile_count = await pool.fetchval("SELECT COUNT(*) FROM tiles WHERE owner_id = $1", discord_id)
    d = dict(row)
    d["tile_count"] = tile_count
    return d

async def register_player(bot, discord_id: int, name: str):
    pool = await get_pool()
    grace_until = datetime.datetime.utcnow() + datetime.timedelta(days=3)
    await pool.execute(
        """INSERT INTO players (discord_id, name, gold, food, materials, influence, grace_until)
           VALUES ($1, $2, $3, $4, $5, $6, $7)
           ON CONFLICT DO NOTHING""",
        discord_id, name, START_GOLD, START_FOOD, START_MATERIALS, START_INFLUENCE, grace_until
    )

async def adjust_resources(bot, discord_id: int, gold=0, food=0, materials=0, influence=0):
    pool = await get_pool()
    await pool.execute(
        """UPDATE players SET
           gold      = gold + $2,
           food      = food + $3,
           materials = materials + $4,
           influence = influence + $5
           WHERE discord_id = $1""",
        discord_id, gold, food, materials, influence
    )

async def get_leaderboard(bot):
    pool = await get_pool()
    rows = await pool.fetch("SELECT name, prestige FROM players ORDER BY prestige DESC LIMIT 20")
    return [dict(r) for r in rows]

async def is_in_grace(bot, discord_id: int) -> bool:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT grace_until FROM players WHERE discord_id = $1", discord_id)
    if not row or not row["grace_until"]:
        return False
    return datetime.datetime.utcnow() < row["grace_until"]
