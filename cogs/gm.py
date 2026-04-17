import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import is_gm
from utils import embeds
from db.queries.players import register_player
from db.queries.tiles import set_spawn, apply_decay
from db.connection import get_pool
import datetime


async def post_world_event(bot, guild_id: int, embed: discord.Embed):
    cfg = bot.guild_config(guild_id)
    channel_id = await cfg.get_channel("world_events")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)


async def post_gm_alert(bot, guild_id: int, embed: discord.Embed):
    cfg = bot.guild_config(guild_id)
    channel_id = await cfg.get_channel("gm_alerts")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)


class GM(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gm_register", description="Manually register a player into the game")
    @is_gm()
    async def gm_register(self, interaction: discord.Interaction, user: discord.Member, name: str):
        await register_player(self.bot, interaction.guild_id, user.id, name)
        await interaction.response.send_message(
            embed=embeds.success("Player Registered", f"{user.mention} registered as {name}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_set_spawn", description="Mark a tile as a spawn point for new players")
    @is_gm()
    async def gm_set_spawn(self, interaction: discord.Interaction, coord: str, value: bool):
        await set_spawn(self.bot, interaction.guild_id, coord.upper(), value)
        status = "marked" if value else "unmarked"
        await interaction.response.send_message(
            embed=embeds.success("Spawn Updated", f"Tile {coord.upper()} {status} as spawn point."),
            ephemeral=True
        )

    @app_commands.command(name="gm_event", description="Post a world event to #world-events")
    @is_gm()
    async def gm_event(self, interaction: discord.Interaction, title: str, description: str):
        embed = embeds.gm_event(title, description)
        await post_world_event(self.bot, interaction.guild_id, embed)
        await interaction.response.send_message(embed=embeds.success("Event Posted"), ephemeral=True)

    @app_commands.command(name="gm_decay", description="Manually apply dev decay to a tile")
    @is_gm()
    async def gm_decay(self, interaction: discord.Interaction, coord: str, amount: int):
        await apply_decay(self.bot, interaction.guild_id, coord.upper(), amount)
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
        await pool.execute(
            f"UPDATE players SET {col} = {col} + $1 WHERE guild_id = $2 AND discord_id = $3",
            amount, interaction.guild_id, user.id
        )
        await interaction.response.send_message(
            embed=embeds.success("Resources Given", f"+{amount} {resource} given to {user.display_name}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_pause", description="Pause or unpause the turn ticker")
    @is_gm()
    async def gm_pause(self, interaction: discord.Interaction, paused: bool):
        pool = await get_pool()
        await pool.execute(
            """INSERT INTO game_state (guild_id, key, value) VALUES ($1, 'paused', $2)
               ON CONFLICT (guild_id, key) DO UPDATE SET value = EXCLUDED.value""",
            interaction.guild_id, str(paused).lower()
        )
        status = "paused" if paused else "resumed"
        await interaction.response.send_message(
            embed=embeds.warning("Game " + status.title(), f"Turn ticker {status}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_set_tile_name", description="Name a tile on the map")
    @is_gm()
    async def gm_set_tile_name(self, interaction: discord.Interaction, coord: str, name: str):
        pool = await get_pool()
        await pool.execute(
            "UPDATE tiles SET name = $1 WHERE guild_id = $2 AND coord = $3",
            name, interaction.guild_id, coord.upper()
        )
        await interaction.response.send_message(
            embed=embeds.success("Tile Named", f"{coord.upper()} is now called {name}."),
            ephemeral=True
        )

    @app_commands.command(name="gm_seed_map", description="Seed blank 64×64 map for this server (safe to re-run)")
    @is_gm()
    async def gm_seed_map(self, interaction: discord.Interaction):
        from db.queries.tiles import ensure_guild_map
        await interaction.response.defer(ephemeral=True)
        await ensure_guild_map(interaction.guild_id)
        await interaction.followup.send(
            embed=embeds.success("Map Ready", "64×64 blank map ensured for this server."),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(GM(bot))
