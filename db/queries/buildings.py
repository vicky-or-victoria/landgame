from db.connection import get_pool


async def get_buildings(bot, guild_id: int, coord: str):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM buildings WHERE guild_id = $1 AND coord = $2",
        guild_id, coord
    )
    return [dict(r) for r in rows]
