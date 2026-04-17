from db.connection import get_pool


async def get_armies(bot, guild_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT * FROM armies WHERE guild_id = $1 AND owner_id = $2",
        guild_id, discord_id
    )
    return [dict(r) for r in rows]
            await pool.execute("UPDATE frontlines SET defender_army = $1 WHERE id = $2", army_id, existing["id"])
    else:
        await pool.execute(
            "INSERT INTO frontlines (tile_coord, attacker_id, attacker_army) VALUES ($1, $2, $3)",
            tile_coord, discord_id, army_id
        )
    return True
