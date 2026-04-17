from db.connection import get_pool
from config import TAX_BASE_RATE, TRADE_ROUTE_DEV_SCALE

async def collect_tax(bot, discord_id: int) -> str:
    pool = await get_pool()
    tiles = await pool.fetch("SELECT coord, dev, terrain FROM tiles WHERE owner_id = $1", discord_id)
    total_gold = 0
    total_food = 0
    for tile in tiles:
        gold = int(tile["dev"] * TAX_BASE_RATE * 100)
        food = int(tile["dev"] * 0.005 * 100)
        if tile["terrain"] in ("river", "coastal"):
            gold += int(tile["dev"] * TRADE_ROUTE_DEV_SCALE * 100)
        total_gold += gold
        total_food += food
    await pool.execute(
        "UPDATE players SET gold = gold + $1, food = food + $2 WHERE discord_id = $3",
        total_gold, total_food, discord_id
    )
    return f"+{total_gold} gold, +{total_food} food collected from {len(tiles)} tiles."

async def post_market_order(bot, discord_id: int, resource: str, amount: int, price: int, order_type: str):
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO market_orders (player_id, resource, amount, price, order_type)
           VALUES ($1, $2, $3, $4, $5)""",
        discord_id, resource, amount, price, order_type
    )

async def get_market_orders(bot, resource: str = None):
    pool = await get_pool()
    if resource:
        rows = await pool.fetch(
            "SELECT * FROM market_orders WHERE filled = FALSE AND resource = $1 ORDER BY price", resource
        )
    else:
        rows = await pool.fetch("SELECT * FROM market_orders WHERE filled = FALSE ORDER BY resource, price")
    return [dict(r) for r in rows]

async def transfer_resources(bot, from_id: int, to_id: int, resource: str, amount: int) -> bool:
    pool = await get_pool()
    col = resource.lower()
    if col not in ("gold", "food", "materials"):
        return False
    sender = await pool.fetchrow(f"SELECT {col} FROM players WHERE discord_id = $1", from_id)
    if not sender or sender[col] < amount:
        return False
    await pool.execute(f"UPDATE players SET {col} = {col} - $1 WHERE discord_id = $2", amount, from_id)
    await pool.execute(f"UPDATE players SET {col} = {col} + $1 WHERE discord_id = $2", amount, to_id)
    return True
