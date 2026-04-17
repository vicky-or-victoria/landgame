import discord
from discord.ext import commands
from utils import embeds
from db.queries.economy import collect_tax, post_market_order, transfer_resources
from db.queries.diplomacy import get_player_by_name


async def post_public(bot, guild_id: int, mention: str, embed: discord.Embed):
    cfg = bot.guild_config(guild_id)
    channel_id = await cfg.get_channel("commands")
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(content=mention, embed=embed)


async def handle_market_order(interaction: discord.Interaction, resource: str, amount: int, price: int, order_type: str):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    resource = resource.lower()
    order_type = order_type.lower()
    if resource not in ("gold", "food", "materials"):
        await interaction.followup.send(embed=embeds.error("Invalid Resource", "Must be gold, food, or materials."), ephemeral=True)
        return
    if order_type not in ("buy", "sell"):
        await interaction.followup.send(embed=embeds.error("Invalid Order Type", "Must be buy or sell."), ephemeral=True)
        return
    await post_market_order(bot, guild_id, interaction.user.id, resource, amount, price, order_type)
    await interaction.followup.send(embed=embeds.success("Order Posted", f"{order_type.title()} {amount} {resource} at {price} each."), ephemeral=True)
    await post_public(bot, guild_id, interaction.user.mention, embeds.info(f"Market Order — {resource.title()}", f"{interaction.user.display_name} posted: {order_type} {amount} {resource} @ {price} each."))


async def handle_trade(interaction: discord.Interaction, target_name: str, resource: str, amount: int):
    await interaction.response.defer(ephemeral=True)
    bot = interaction.client
    guild_id = interaction.guild_id
    target = await get_player_by_name(bot, guild_id, target_name)
    if not target:
        await interaction.followup.send(embed=embeds.error("Player Not Found", f"No player named {target_name}."), ephemeral=True)
        return
    success = await transfer_resources(bot, guild_id, interaction.user.id, target["discord_id"], resource, amount)
    if not success:
        await interaction.followup.send(embed=embeds.error("Transfer Failed", "Insufficient resources or invalid resource."), ephemeral=True)
        return
    await interaction.followup.send(embed=embeds.success("Trade Complete", f"Sent {amount} {resource} to {target_name}."), ephemeral=True)
    target_user = bot.get_user(target["discord_id"])
    mention = target_user.mention if target_user else target_name
    await post_public(bot, guild_id, mention, embeds.success("Trade", f"{interaction.user.display_name} sent {amount} {resource} to {target_name}."))


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Economy(bot))
