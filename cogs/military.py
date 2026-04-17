import discord
from discord.ext import commands
from utils import embeds
from db.queries import tiles as tile_queries, players as player_queries
from db.queries.military import raise_levy, move_army, assign_to_front
from config import LEVY_DEV_RATIO


async def post_public(bot, guild_id: int, mention: str, embed: discord.Embed):
    cfg = bot.guild_config(guild_id)
    channel_id = await cfg.get_channel("commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=mention, embed=embed)


async def handle_raise_levy(interaction: discord.Interaction, coord: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    tile = await tile_queries.get_tile(bot, guild_id, coord)
    if not tile or tile["owner_id"] != interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Not Your Tile", f"You do not own {coord}."), ephemeral=True)
        return
    levy_size = tile["dev"] * LEVY_DEV_RATIO
    if levy_size < 1:
        await interaction.followup.send(embed=embeds.error("Dev Too Low", "Develop this tile further before raising a levy."), ephemeral=True)
        return
    army_id = await raise_levy(bot, guild_id, interaction.user.id, coord, levy_size)
    await interaction.followup.send(embed=embeds.success("Levy Raised", f"Army #{army_id} raised at {coord} with {levy_size} troops."), ephemeral=True)
    await post_public(bot, guild_id, interaction.user.mention, embeds.success(f"Levy Raised — {coord}", f"{interaction.user.display_name} raised a levy of {levy_size} at {coord}."))


async def handle_move_army(interaction: discord.Interaction, army_id: int, coord: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    tile = await tile_queries.get_tile(bot, guild_id, coord)
    if not tile:
        await interaction.followup.send(embed=embeds.error("Invalid Tile", f"Tile {coord} does not exist."), ephemeral=True)
        return
    moved = await move_army(bot, guild_id, army_id, interaction.user.id, coord)
    if not moved:
        await interaction.followup.send(embed=embeds.error("Failed", "Army not found or not yours."), ephemeral=True)
        return
    await interaction.followup.send(embed=embeds.success("Army Moved", f"Army #{army_id} moved to {coord}."), ephemeral=True)
    await post_public(bot, guild_id, interaction.user.mention, embeds.success(f"Army Moved — {coord}", f"{interaction.user.display_name} moved Army #{army_id} to {coord}."))


async def handle_assign_front(interaction: discord.Interaction, army_id: int, coord: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    assigned = await assign_to_front(bot, guild_id, army_id, interaction.user.id, coord)
    if not assigned:
        await interaction.followup.send(embed=embeds.error("Failed", "Could not assign army to that front."), ephemeral=True)
        return
    await interaction.followup.send(embed=embeds.success("Assigned to Front", f"Army #{army_id} assigned to frontline at {coord}."), ephemeral=True)
    await post_public(bot, guild_id, interaction.user.mention, embeds.battle(f"Front Established — {coord}", f"{interaction.user.display_name} assigned Army #{army_id} to the front at {coord}."))


class Military(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Military(bot))
