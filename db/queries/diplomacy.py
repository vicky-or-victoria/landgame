from db.connection import get_pool


async def get_treaties(bot, guild_id: int, discord_id: int):
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT d.*,
                  CASE WHEN d.proposer_id = $2 THEN p2.name ELSE p1.name END AS other
           FROM diplomacy d
           LEFT JOIN players p1 ON p1.guild_id = $1 AND p1.discord_id = d.proposer_id
           LEFT JOIN players p2 ON p2.guild_id = $1 AND p2.discord_id = d.target_id
           WHERE d.guild_id = $1 AND (d.proposer_id = $2 OR d.target_id = $2)
             AND d.status != 'rejected'""",
        guild_id, discord_id
    )
    return [dict(r) for r in rows]
