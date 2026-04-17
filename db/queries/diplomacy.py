from db.connection import get_pool
import datetime

async def offer_treaty(bot, from_id: int, to_id: int, treaty_type: str):
    pool = await get_pool()
    await pool.execute(
        "INSERT INTO treaties (player_a, player_b, treaty_type, status) VALUES ($1, $2, $3, 'pending')",
        from_id, to_id, treaty_type
    )

async def get_treaties(bot, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT t.*, p.name AS other
           FROM treaties t
           JOIN players p ON (
               CASE WHEN t.player_a = $1 THEN t.player_b ELSE t.player_a END = p.discord_id
           )
           WHERE (t.player_a = $1 OR t.player_b = $1) AND t.status != 'rejected'""",
        discord_id
    )
    return [dict(r) for r in rows]

async def resolve_treaty(bot, treaty_id: int, status: str):
    pool = await get_pool()
    await pool.execute(
        "UPDATE treaties SET status = $1, resolved_at = $2 WHERE id = $3",
        status, datetime.datetime.utcnow(), treaty_id
    )

async def declare_war(bot, attacker_id: int, defender_id: int):
    pool = await get_pool()
    existing = await pool.fetchrow(
        "SELECT id FROM wars WHERE attacker_id = $1 AND defender_id = $2 AND active = TRUE",
        attacker_id, defender_id
    )
    if existing:
        return False
    hostilities_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    await pool.execute(
        "INSERT INTO wars (attacker_id, defender_id, hostilities_at) VALUES ($1, $2, $3)",
        attacker_id, defender_id, hostilities_at
    )
    return True

async def get_active_war(bot, player_a: int, player_b: int):
    pool = await get_pool()
    row = await pool.fetchrow(
        """SELECT * FROM wars WHERE active = TRUE AND (
           (attacker_id = $1 AND defender_id = $2) OR
           (attacker_id = $2 AND defender_id = $1)
        )""",
        player_a, player_b
    )
    return dict(row) if row else None

async def get_player_by_name(bot, name: str):
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM players WHERE LOWER(name) = LOWER($1)", name)
    return dict(row) if row else None
