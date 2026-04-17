from utils import embeds

async def log_action(bot, event_type: str, target: str, description: str):
    pool_import = __import__("db.connection", fromlist=["get_pool"])
    pool = await pool_import.get_pool()
    turn_row = await pool.fetchrow("SELECT value FROM game_state WHERE key = 'turn'")
    turn = int(turn_row["value"]) if turn_row else 0
    await pool.execute(
        "INSERT INTO events_log (turn, event_type, target, description) VALUES ($1, $2, $3, $4)",
        turn, event_type, target, description
    )
    channel_id = bot.config.get_channel("public_log")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            e = embeds.info(f"{event_type} — {target}", description)
            await channel.send(embed=e)

async def alert_gm(bot, title: str, description: str):
    channel_id = bot.config.get_channel("gm_alerts")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embeds.warning(title, description))
