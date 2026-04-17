import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import is_gm
from utils import embeds
from db.queries.players import register_player
from db.queries.tiles import set_spawn, apply_decay, get_all_tiles
from db.connection import get_pool
import datetime

async def post_world_event(bot, embed: discord.Embed):
    channel_id = bot.config.get_channel("world_events")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

async def post_gm_alert(bot, embed: discord.Embed):
    channel_id = bot.config.get_channel("gm_alerts")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

class GM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gm_register", description="Register a player into the game")
    @is_gm()
    async def gm_register(self, interaction: discord.Interaction, user: discord.Member, name: str):
        await register_player(self.bot, user.id, name)
        await interaction.response.send_message(
            embed=embeds.success("Player Registered", f"{user.mention} registered as {name}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_set_spawn", description="Mark a tile as a spawn point for new players")
    @is_gm()
    async def gm_set_spawn(self, interaction: discord.Interaction, coord: str, value: bool):
        await set_spawn(self.bot, coord.upper(), value)
        status = "marked" if value else "unmarked"
        await interaction.response.send_message(
            embed=embeds.success("Spawn Updated", f"Tile {coord.upper()} {status} as spawn point."),
            ephemeral=True
        )

    @app_commands.command(name="gm_event", description="Post a world event to #world-events")
    @is_gm()
    async def gm_event(self, interaction: discord.Interaction, title: str, description: str):
        embed = embeds.gm_event(title, description)
        await post_world_event(self.bot, embed)
        await interaction.response.send_message(embed=embeds.success("Event Posted"), ephemeral=True)

    @app_commands.command(name="gm_decay", description="Manually apply dev decay to a tile")
    @is_gm()
    async def gm_decay(self, interaction: discord.Interaction, coord: str, amount: int):
        await apply_decay(self.bot, coord.upper(), amount)
        await interaction.response.send_message(
            embed=embeds.success("Decay Applied", f"Tile {coord.upper()} lost {amount} dev."),
            ephemeral=True
        )

    @app_commands.command(name="gm_give", description="Give resources to a player")
    @is_gm()
    async def gm_give(self, interaction: discord.Interaction, user: discord.Member, resource: str, amount: int):
        pool = await get_pool()
        col = resource.lower()
        if col not in ("gold", "food", "materials", "influence"):
            await interaction.response.send_message(embed=embeds.error("Invalid Resource"), ephemeral=True)
            return
        await pool.execute(f"UPDATE players SET {col} = {col} + $1 WHERE discord_id = $2", amount, user.id)
        await interaction.response.send_message(
            embed=embeds.success("Resources Given", f"+{amount} {resource} given to {user.display_name}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_pause", description="Pause or unpause the turn ticker")
    @is_gm()
    async def gm_pause(self, interaction: discord.Interaction, paused: bool):
        pool = await get_pool()
        await pool.execute("UPDATE game_state SET value = $1 WHERE key = 'paused'", str(paused).lower())
        status = "paused" if paused else "resumed"
        await interaction.response.send_message(embed=embeds.warning("Game " + status.title(), f"Turn ticker {status}."), ephemeral=True)

    @app_commands.command(name="gm_set_tile_name", description="Name a tile on the map")
    @is_gm()
    async def gm_set_tile_name(self, interaction: discord.Interaction, coord: str, name: str):
        pool = await get_pool()
        await pool.execute("UPDATE tiles SET name = $1 WHERE coord = $2", name, coord.upper())
        await interaction.response.send_message(
            embed=embeds.success("Tile Named", f"{coord.upper()} is now called {name}."),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(GM(bot))
