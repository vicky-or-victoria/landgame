import discord
from discord.ext import commands
from utils import embeds
from db.queries.tiles import get_tile
from db.queries.buildings import get_buildings
from config import TERRAIN_SLOTS


async def handle_inspect_tile(interaction: discord.Interaction, coord: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    tile = await get_tile(bot, guild_id, coord)
    if not tile:
        await interaction.followup.send(embed=embeds.error("Not Found", f"Tile {coord} does not exist."), ephemeral=True)
        return
    buildings = await get_buildings(bot, guild_id, coord)
    owner_name = "Neutral"
    if tile["owner_id"]:
        from db.connection import get_pool
        pool = await get_pool()
        row = await pool.fetchrow(
            "SELECT name FROM players WHERE guild_id = $1 AND discord_id = $2",
            guild_id, tile["owner_id"]
        )
        owner_name = row["name"] if row else "Unknown"
    max_slots = TERRAIN_SLOTS.get(tile["terrain"], 2)
    levy_cap = tile["dev"] * 5
    tax = int(tile["dev"] * 1.5)
    tile_data = {
        "coord":     coord,
        "name":      tile.get("name") or coord,
        "owner":     owner_name,
        "terrain":   tile["terrain"],
        "dev":       tile["dev"],
        "buildings": [{"name": b["name"], "tier": b["tier"]} for b in buildings],
        "max_slots": max_slots,
        "levy_cap":  levy_cap,
        "tax":       tax,
    }
    await interaction.followup.send(embed=embeds.tile_inspect(tile_data), ephemeral=True)


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Info(bot))
