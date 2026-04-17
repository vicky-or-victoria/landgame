import discord
from discord.ext import commands
from utils import embeds
from db.queries.diplomacy import offer_treaty, declare_war, get_player_by_name
from db.queries.players import is_in_grace

async def post_public(bot, mention: str, embed: discord.Embed):
    channel_id = bot.config.get_channel("commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=mention, embed=embed)

async def handle_offer_treaty(interaction: discord.Interaction, target_name: str, treaty_type: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    treaty_type = treaty_type.lower()
    if treaty_type not in ("alliance", "nap", "trade"):
        await interaction.followup.send(embed=embeds.error("Invalid Treaty Type", "Must be alliance, nap, or trade."), ephemeral=True)
        return
    target = await get_player_by_name(bot, target_name)
    if not target:
        await interaction.followup.send(embed=embeds.error("Player Not Found", f"No player named {target_name}."), ephemeral=True)
        return
    if target["discord_id"] == interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Invalid", "You cannot offer a treaty to yourself."), ephemeral=True)
        return
    await offer_treaty(bot, interaction.user.id, target["discord_id"], treaty_type)
    await interaction.followup.send(embed=embeds.success("Treaty Offered", f"{treaty_type.title()} offer sent to {target_name}."), ephemeral=True)
    target_user = bot.get_user(target["discord_id"])
    mention = target_user.mention if target_user else target_name
    await post_public(bot, mention, embeds.info(f"Treaty Offer — {treaty_type.title()}", f"{interaction.user.display_name} offered a {treaty_type} to {target_name}."))

async def handle_declare_war(interaction: discord.Interaction, target_name: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    target = await get_player_by_name(bot, target_name)
    if not target:
        await interaction.followup.send(embed=embeds.error("Player Not Found", f"No player named {target_name}."), ephemeral=True)
        return
    if target["discord_id"] == interaction.user.id:
        await interaction.followup.send(embed=embeds.error("Invalid", "You cannot declare war on yourself."), ephemeral=True)
        return
    if await is_in_grace(bot, target["discord_id"]):
        await interaction.followup.send(embed=embeds.error("Grace Period", f"{target_name} is protected by a new player grace period."), ephemeral=True)
        return
    declared = await declare_war(bot, interaction.user.id, target["discord_id"])
    if not declared:
        await interaction.followup.send(embed=embeds.error("Already at War", f"You are already at war with {target_name}."), ephemeral=True)
        return
    await interaction.followup.send(embed=embeds.warning("War Declared", f"War declared on {target_name}. Hostilities begin in 24 hours."), ephemeral=True)
    target_user = bot.get_user(target["discord_id"])
    mention = target_user.mention if target_user else target_name
    await post_public(bot, mention, embeds.battle(f"War Declared", f"{interaction.user.display_name} has declared war on {target_name}. Hostilities begin in 24 hours."))

class Diplomacy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(Diplomacy(bot))
