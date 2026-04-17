"""
Map renderer — draws the 64×64 grid for a specific guild.
Tiles are stored in the DB (static, non-procedurally generated).
Only tiles that have been named or claimed by players are visually highlighted.
The rest of the grid shows as empty neutral land.
"""
import discord
import io
from PIL import Image, ImageDraw, ImageFont
from db.queries.tiles import get_all_tiles
from renderer.tile_sprites import PLAYER_COLORS, get_tile_color
from renderer.overlay import draw_grid

TILE_SIZE  = 12
MAP_WIDTH  = 64
MAP_HEIGHT = 64

# Color for unclaimed/unnamed tiles
COLOR_NEUTRAL  = (35, 35, 40)
# Grid line color
COLOR_GRID     = (55, 55, 65)


async def render_map(bot, guild_id: int) -> discord.File:
    """Render the 64×64 map for the given guild and return a discord.File."""
    tiles = await get_all_tiles(bot, guild_id)
    tile_map = {t["coord"]: t for t in tiles}

    # Build player → color index map
    from db.connection import get_pool
    pool = await get_pool()
    players = await pool.fetch(
        "SELECT discord_id FROM players WHERE guild_id = $1 ORDER BY registered_at",
        guild_id
    )
    player_color = {
        p["discord_id"]: PLAYER_COLORS[i % len(PLAYER_COLORS)]
        for i, p in enumerate(players)
    }

    img_w = MAP_WIDTH  * TILE_SIZE
    img_h = MAP_HEIGHT * TILE_SIZE
    img   = Image.new("RGB", (img_w, img_h), COLOR_NEUTRAL)
    draw  = ImageDraw.Draw(img)

    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            coord = f"{chr(65 + col)}{row + 1}"
            tile  = tile_map.get(coord)
            x     = col * TILE_SIZE
            y     = row * TILE_SIZE

            if tile and tile.get("owner_id"):
                owner_c = player_color.get(tile["owner_id"])
                color   = get_tile_color(tile.get("terrain", "flat"), owner_c, tile.get("is_spawn", False))
            elif tile and tile.get("terrain") and tile["terrain"] != "flat":
                # Unowned but has a special terrain — show terrain colour with no owner tint
                color = get_tile_color(tile["terrain"], None, tile.get("is_spawn", False))
            else:
                color = COLOR_NEUTRAL

            draw.rectangle(
                [x, y, x + TILE_SIZE - 1, y + TILE_SIZE - 1],
                fill=color
            )

    # Draw coordinate grid lines
    draw_grid(draw)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return discord.File(buf, filename=f"map_{guild_id}.png")
