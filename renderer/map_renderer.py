import discord
import io
from PIL import Image, ImageDraw
from db.queries.tiles import get_all_tiles
from renderer.tile_sprites import PLAYER_COLORS, get_tile_color
from renderer.overlay import draw_grid
from config import MAP_WIDTH, MAP_HEIGHT

TILE_SIZE = 12

async def render_map(bot) -> discord.File:
    tiles = await get_all_tiles(bot)
    tile_map = {t["coord"]: t for t in tiles}

    pool_import = __import__("db.connection", fromlist=["get_pool"])
    pool = await pool_import.get_pool()
    players = await pool.fetch("SELECT discord_id FROM players ORDER BY registered_at")
    player_color = {p["discord_id"]: PLAYER_COLORS[i % len(PLAYER_COLORS)] for i, p in enumerate(players)}

    img_w = MAP_WIDTH  * TILE_SIZE
    img_h = MAP_HEIGHT * TILE_SIZE
    img   = Image.new("RGB", (img_w, img_h), (20, 20, 20))
    draw  = ImageDraw.Draw(img)

    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            coord = f"{chr(65 + col)}{row + 1}"
            tile  = tile_map.get(coord)
            x     = col * TILE_SIZE
            y     = row * TILE_SIZE
            if tile:
                owner_c = player_color.get(tile["owner_id"]) if tile["owner_id"] else None
                color   = get_tile_color(tile["terrain"], owner_c, tile.get("is_spawn", False))
            else:
                color = (20, 20, 20)
            draw.rectangle([x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1], fill=color)

    draw_grid(draw)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename="map.png")
