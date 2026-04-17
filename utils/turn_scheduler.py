import asyncio
from db.connection import get_pool
from db.queries.tiles import get_all_tiles, apply_decay
from config import PASSIVE_DECAY_AMOUNT, CAPTURE_DECAY_RATE

async def is_paused(bot) -> bool:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT value FROM game_state WHERE key = 'paused'")
    return row and row["value"] == "true"

async def get_turn_interval(bot) -> int:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT value FROM game_state WHERE key = 'turn_interval_hours'")
    return int(row["value"]) if row else 24

async def increment_turn(bot) -> int:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT value FROM game_state WHERE key = 'turn'")
    turn = int(row["value"]) + 1
    await pool.execute("UPDATE game_state SET value = $1 WHERE key = 'turn'", str(turn))
    return turn

async def run_decay(bot):
    tiles = await get_all_tiles(bot)
    for tile in tiles:
        if not tile["owner_id"]:
            continue
        if tile.get("stabilized") is False:
            await apply_decay(bot, tile["coord"], CAPTURE_DECAY_RATE)
        else:
            await apply_decay(bot, tile["coord"], PASSIVE_DECAY_AMOUNT)

async def post_turn_log(bot, turn: int):
    channel_id = bot.config.get_channel("turn_log")
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if channel:
        from utils import embeds
        await channel.send(embed=embeds.info(f"Turn {turn} Complete", "Decay applied. Tax not auto-collected."))

async def turn_loop(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        interval = await get_turn_interval(bot)
        await asyncio.sleep(interval * 3600)
        if await is_paused(bot):
            continue
        turn = await increment_turn(bot)
        await run_decay(bot)
        await post_turn_log(bot, turn)
