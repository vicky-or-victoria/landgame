from db.connection import get_pool
from config import TAX_BASE_RATE


async def collect_tax(bot, guild_id: int, discord_id: int):
    pool = await get_pool()
    player = await pool.fetchrow(
        "SELECT * FROM players WHERE guild_id = $1 AND discord_id = $2",
        guild_id, discord_id
    )
    if not player:
        return "Player not found."
    tile_count = await pool.fetchval(
        "SELECT COUNT(*) FROM tiles WHERE guild_id = $1 AND owner_id = $2",
        guild_id, discord_id
    )
    income = int((tile_count or 0) * player["gold"] * TAX_BASE_RATE)
    await pool.execute(
        "UPDATE players SET gold = gold + $1 WHERE guild_id = $2 AND discord_id = $3",
        income, guild_id, discord_id
    )
    return f"Collected {income} gold from {tile_count} tiles."
