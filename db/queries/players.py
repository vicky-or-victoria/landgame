from db.connection import get_pool
from config import START_GOLD, START_FOOD, START_MATERIALS, START_INFLUENCE
import datetime


async def get_player(bot, guild_id: int, discord_id: int):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM players WHERE guild_id = $1 AND discord_id = $2",
        guild_id, discord_id
    )
    if not row:
        return None
    tile_count = await pool.fetchval(
        "SELECT COUNT(*) FROM tiles WHERE guild_id = $1 AND owner_id = $2",
        guild_id, discord_id
    )
    d = dict(row)
    d["tile_count"] = tile_count
    return d


async def register_player(bot, guild_id: int, discord_id: int, name: str):
    pool = await get_pool()
    grace_until = datetime.datetime.utcnow() + datetime.timedelta(days=3)
    await pool.execute(
        """INSERT INTO players (guild_id, discord_id, name, gold, food, materials, influence, grace_until)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
           ON CONFLICT DO NOTHING""",
        guild_id, discord_id, name,
        START_GOLD, START_FOOD, START_MATERIALS, START_INFLUENCE,
        grace_until
    )


async def adjust_resources(bot, guild_id: int, discord_id: int, gold=0, food=0, materials=0, influence=0):
    pool = await get_pool()
    await pool.execute(
        """UPDATE players SET
           gold      = gold + $3,
           food      = food + $4,
           materials = materials + $5,
           influence = influence + $6
           WHERE guild_id = $1 AND discord_id = $2""",
        guild_id, discord_id, gold, food, materials, influence
    )


async def get_leaderboard(bot, guild_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT name, prestige FROM players WHERE guild_id = $1 ORDER BY prestige DESC LIMIT 20",
        guild_id
    )
    return [dict(r) for r in rows]


async def is_in_grace(bot, guild_id: int, discord_id: int) -> bool:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT grace_until FROM players WHERE guild_id = $1 AND discord_id = $2",
        guild_id, discord_id
    )
    if not row or not row["grace_until"]:
        return False
    return datetime.datetime.utcnow() < row["grace_until"]


async def count_players(guild_id: int) -> int:
    pool = await get_pool()
    return await pool.fetchval(
        "SELECT COUNT(*) FROM players WHERE guild_id = $1", guild_id
    ) or 0
