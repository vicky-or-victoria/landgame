import asyncio
import asyncpg
import os
import glob
from dotenv import load_dotenv

load_dotenv()

async def run():
    conn = await asyncpg.connect(dsn=os.getenv("DATABASE_URL"))
    files = sorted(glob.glob("db/migrations/*.sql"))
    for path in files:
        with open(path) as f:
            sql = f.read()
        await conn.execute(sql)
        print(f"Ran {path}")
    await conn.close()
    print("Done.")

asyncio.run(run())
