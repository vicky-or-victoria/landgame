import asyncio
import asyncpg
import os
import random
from dotenv import load_dotenv
load_dotenv()
MAP_WIDTH  = 64
MAP_HEIGHT = 64
TERRAIN_WEIGHTS = [
    ("flat",     30),
    ("hilly",    15),
    ("forest",   15),
    ("mountain", 10),
    ("river",     8),
    ("coastal",   7),
    ("desert",    6),
    ("ruins",     3),
    ("cursed",    2),
    ("sacred",    1),
    ("leyline",   1),
    ("volcanic",  1),
    ("fortress",  1),
]
TERRAINS   = [t for t, _ in TERRAIN_WEIGHTS]
WEIGHTS    = [w for _, w in TERRAIN_WEIGHTS]
def pick_terrain(col: int, row: int) -> str:
    edge = col == 0 or col == MAP_WIDTH - 1 or row == 0 or row == MAP_HEIGHT - 1
    if edge:
        return random.choices(["coastal", "mountain", "hilly"], weights=[40, 35, 25])[0]
    return random.choices(TERRAINS, weights=WEIGHTS)[0]
async def seed():
    conn = await asyncpg.connect(dsn=os.getenv("DATABASE_URL"))
    records = []
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            coord   = f"{chr(65 + col)}{row + 1}"
            terrain = pick_terrain(col, row)
            records.append((coord, terrain))
    await conn.executemany(
        "INSERT INTO tiles (coord, terrain) VALUES ($1, $2) ON CONFLICT DO NOTHING",
        records
    )
    await conn.close()
    print(f"Seeded {len(records)} tiles.")
asyncio.run(seed())
