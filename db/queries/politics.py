from db.connection import get_pool

async def get_research(bot, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM research WHERE player_id = $1", discord_id)
    return [dict(r) for r in rows]

async def unlock_research(bot, discord_id: int, research_id: str) -> bool:
    pool = await get_pool()
    existing = await pool.fetchrow(
        "SELECT id FROM research WHERE player_id = $1 AND research_id = $2", discord_id, research_id
    )
    if existing:
        return False
    await pool.execute(
        "INSERT INTO research (player_id, research_id) VALUES ($1, $2)", discord_id, research_id
    )
    return True

async def get_traditions(bot, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch("SELECT * FROM traditions WHERE player_id = $1", discord_id)
    return [dict(r) for r in rows]

async def unlock_tradition(bot, discord_id: int, tradition_id: str) -> bool:
    pool = await get_pool()
    existing = await pool.fetchrow(
        "SELECT id FROM traditions WHERE player_id = $1 AND tradition_id = $2", discord_id, tradition_id
    )
    if existing:
        return False
    await pool.execute(
        "INSERT INTO traditions (player_id, tradition_id) VALUES ($1, $2)", discord_id, tradition_id
    )
    return True

async def has_research(bot, discord_id: int, research_id: str) -> bool:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT id FROM research WHERE player_id = $1 AND research_id = $2", discord_id, research_id
    )
    return row is not None
