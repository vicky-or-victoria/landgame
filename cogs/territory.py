import discord
from discord.ext import commands
from utils import embeds
from db.queries import players as player_queries, tiles as tile_queries
from config import TERRAIN_SLOTS, CAPTURE_DEV_PENALTY, CLAIM_COST
import datetime


async def post_public(bot, guild_id: int, content: str, embed: discord.Embed):
    cfg = bot.guild_config(guild_id)
    channel_id = await cfg.get_channel("commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=content, embed=embed)


async def handle_claim(interaction: discord.Interaction, coord: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    tile = await tile_queries.get_tile(bot, guild_id, coord)
    if not tile:
        await interaction.followup.send(embed=embeds.error("Tile Not Found", f"Tile {coord} does not exist."), ephemeral=True)
        return
    if tile["owner_id"]:
        await interaction.followup.send(embed=embeds.error("Already Owned", f"Tile {coord} is already owned."), ephemeral=True)
        return
    player = await player_queries.get_player(bot, guild_id, interaction.user.id)
    if not player:
        await interaction.followup.send(embed=embeds.error("Not Registered", "You are not a registered player."), ephemeral=True)
        return
    cost = CLAIM_COST.get(tile["terrain"], 100)
    if player["gold"] < cost:
        await interaction.followup.send(embed=embeds.error("Insufficient Gold", f"Claiming {coord} costs {cost} gold."), ephemeral=True)
        return
    await tile_queries.set_owner(bot, guild_id, coord, interaction.user.id)
    await player_queries.adjust_resources(bot, guild_id, interaction.user.id, gold=-cost)
    await interaction.followup.send(embed=embeds.success("Tile Claimed", f"You claimed {coord} for {cost} gold."), ephemeral=True)
    await post_public(bot, guild_id, interaction.user.mention, embeds.success(f"Tile Claimed — {coord}", f"{interaction.user.display_name} claimed tile {coord}."))


async def handle_develop(interaction: discord.Interaction, coord: str, amount: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    tile = await tile_queries.get_tile(bot, guild_id, coord)
    if not tile or tile["owner_id"] != interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Not Your Tile", f"You do not own {coord}."), ephemeral=True)
        return
    player = await player_queries.get_player(bot, guild_id, interaction.user.id)
    if player["gold"] < amount:
        await interaction.followup.send(embed=embeds.error("Insufficient Gold", f"You need {amount} gold."), ephemeral=True)
        return
    dev_gain = amount // 20
    await tile_queries.adjust_dev(bot, guild_id, coord, dev_gain)
    await player_queries.adjust_resources(bot, guild_id, interaction.user.id, gold=-amount)
    await interaction.followup.send(embed=embeds.success("Tile Developed", f"{coord} gained +{dev_gain} dev."), ephemeral=True)
    await post_public(bot, guild_id, interaction.user.mention, embeds.success(f"Development — {coord}", f"{interaction.user.display_name} invested {amount} gold into {coord}."))


async def handle_build(interaction: discord.Interaction, coord: str, building_name: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    tile = await tile_queries.get_tile(bot, guild_id, coord)
    if not tile or tile["owner_id"] != interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Not Your Tile", f"You do not own {coord}."), ephemeral=True)
        return
    from db.queries.buildings import get_buildings, add_building
    buildings = await get_buildings(bot, guild_id, coord)
    max_slots = TERRAIN_SLOTS.get(tile["terrain"], 2)
    if len(buildings) >= max_slots:
        await interaction.followup.send(embed=embeds.error("No Slots", f"{coord} has no free building slots."), ephemeral=True)
        return
    await add_building(bot, guild_id, coord, building_name)
    await interaction.followup.send(embed=embeds.success("Building Constructed", f"{building_name} built on {coord}."), ephemeral=True)
    await post_public(bot, guild_id, interaction.user.mention, embeds.success(f"Construction — {coord}", f"{interaction.user.display_name} built {building_name} on {coord}."))


async def handle_demolish(interaction: discord.Interaction, coord: str, building_name: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    tile = await tile_queries.get_tile(bot, guild_id, coord)
    if not tile or tile["owner_id"] != interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Not Your Tile", f"You do not own {coord}."), ephemeral=True)
        return
    from db.queries.buildings import remove_building
    removed = await remove_building(bot, guild_id, coord, building_name)
    if not removed:
        await interaction.followup.send(embed=embeds.error("Not Found", f"No building named {building_name} on {coord}."), ephemeral=True)
        return
    await interaction.followup.send(embed=embeds.success("Building Demolished", f"{building_name} removed from {coord}."), ephemeral=True)
    await post_public(bot, guild_id, interaction.user.mention, embeds.success(f"Demolition — {coord}", f"{interaction.user.display_name} demolished {building_name} on {coord}."))


class Territory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Territory(bot))
