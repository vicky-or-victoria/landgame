from db.connection import get_pool


async def get_traditions(bot, guild_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM traditions WHERE guild_id = $1 AND discord_id = $2",
        guild_id, discord_id
    )
    return [dict(r) for r in rows]
