from db.connection import get_pool


async def get_armies(bot, guild_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT a.id, a.name, a.location,
           COALESCE(SUM(u.size), 0) AS size
           FROM armies a
           LEFT JOIN units u ON u.army_id = a.id AND u.guild_id = $1
           WHERE a.guild_id = $1 AND a.owner_id = $2
           GROUP BY a.id""",
        guild_id, discord_id
    )
    return [dict(r) for r in rows]


async def get_army(bot, guild_id: int, army_id: int):
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM armies WHERE guild_id = $1 AND id = $2",
        guild_id, army_id
    )
    return dict(row) if row else None


async def create_army(bot, guild_id: int, discord_id: int, name: str, location: str) -> int:
    pool = await get_pool()
    row = await pool.fetchrow(
        "INSERT INTO armies (guild_id, owner_id, name, location) VALUES ($1, $2, $3, $4) RETURNING id",
        guild_id, discord_id, name, location
    )
    return row["id"]


async def move_army(bot, guild_id: int, army_id: int, discord_id: int, coord: str) -> bool:
    pool = await get_pool()
    result = await pool.execute(
        "UPDATE armies SET location = $1 WHERE guild_id = $2 AND id = $3 AND owner_id = $4",
        coord, guild_id, army_id, discord_id
    )
    return result != "UPDATE 0"


async def raise_levy(bot, guild_id: int, discord_id: int, tile_coord: str, size: int) -> int:
    pool = await get_pool()
    army_id = await create_army(bot, guild_id, discord_id, f"Levy at {tile_coord}", tile_coord)
    await pool.execute(
        """INSERT INTO units (guild_id, owner_id, home_tile, unit_type, size, is_levy, current_tile, army_id)
           VALUES ($1, $2, $3, 'levy', $4, TRUE, $3, $5)""",
        guild_id, discord_id, tile_coord, size, army_id
    )
    return army_id


async def assign_to_front(bot, guild_id: int, army_id: int, discord_id: int, tile_coord: str):
    pool = await get_pool()
    army = await get_army(bot, guild_id, army_id)
    if not army or army["owner_id"] != discord_id:
        return False
    existing = await pool.fetchrow(
        "SELECT * FROM frontlines WHERE guild_id = $1 AND tile_coord = $2 AND resolved = FALSE",
        guild_id, tile_coord
    )
    if existing:
        if existing["attacker_id"] == discord_id:
            await pool.execute(
                "UPDATE frontlines SET attacker_army = $1 WHERE id = $2",
                army_id, existing["id"]
            )
        else:
            await pool.execute(
                "UPDATE frontlines SET defender_army = $1 WHERE id = $2",
                army_id, existing["id"]
            )
    else:
        await pool.execute(
            "INSERT INTO frontlines (guild_id, tile_coord, attacker_id, attacker_army) VALUES ($1, $2, $3, $4)",
            guild_id, tile_coord, discord_id, army_id
        )
    return True
