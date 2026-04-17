import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import is_owner
from utils import embeds

CHANNEL_NAMES = [
    "world_map", "world_events", "turn_log", "menu",
    "commands", "battle_reports", "leaderboard", "public_log", "gm_alerts"
]


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _cfg(self, interaction: discord.Interaction):
        return self.bot.guild_config(interaction.guild_id)

    @app_commands.command(name="setup_channel", description="Assign a bot channel")
    @is_owner()
    async def setup_channel(self, interaction: discord.Interaction, channel_type: str, channel: discord.TextChannel):
        if channel_type not in CHANNEL_NAMES:
            await interaction.response.send_message(
                embed=embeds.error("Invalid channel type", f"Valid types: {', '.join(CHANNEL_NAMES)}"),
                ephemeral=True
            )
            return
        cfg = self._cfg(interaction)
        await cfg.set_channel(channel_type, channel.id)
        missing = await cfg.get_missing_channels()
        if not missing and await cfg.get_gm_role():
            await cfg.mark_setup_complete()
        await interaction.response.send_message(
            embed=embeds.success("Channel Set", f"{channel_type} → {channel.mention}"),
            ephemeral=True
        )

    @app_commands.command(name="setup_gmrole", description="Assign the GM role")
    @is_owner()
    async def setup_gmrole(self, interaction: discord.Interaction, role: discord.Role):
        cfg = self._cfg(interaction)
        await cfg.set_gm_role(role.id)
        missing = await cfg.get_missing_channels()
        if not missing:
            await cfg.mark_setup_complete()
        await interaction.response.send_message(
            embed=embeds.success("GM Role Set", f"{role.mention} is now the GM role"),
            ephemeral=True
        )

    @app_commands.command(name="setup_playerrole", description="Set the role granted on player registration")
    @is_owner()
    async def setup_playerrole(self, interaction: discord.Interaction, role: discord.Role):
        cfg = self._cfg(interaction)
        await cfg.set_player_role(role.id)
        await interaction.response.send_message(
            embed=embeds.success("Player Role Set", f"{role.mention} will be granted upon registration."),
            ephemeral=True
        )

    @app_commands.command(name="setup_status", description="Check setup progress")
    @is_owner()
    async def setup_status(self, interaction: discord.Interaction):
        cfg = self._cfg(interaction)
        missing = await cfg.get_missing_channels()
        gm_role = await cfg.get_gm_role()
        player_role = await cfg.get_player_role()
        lines = []
        for name in CHANNEL_NAMES:
            val = await cfg.get_channel(name)
            lines.append(f"{name}: {'✅ set' if val else '❌ missing'}")
        lines.append(f"gm_role: {'✅ set' if gm_role else '❌ missing'}")
        lines.append(f"player_role: {'✅ set' if player_role else '⚠️ not set'}")
        lines.append(f"setup_complete: {'✅' if await cfg.is_setup_complete() else '❌'}")
        await interaction.response.send_message(
            embed=embeds.info("Setup Status", "\n".join(lines)),
            ephemeral=True
        )

    @app_commands.command(name="setup_reset", description="Wipe all config for this server and start fresh")
    @is_owner()
    async def setup_reset(self, interaction: discord.Interaction):
        from db.connection import get_pool
        pool = await get_pool()
        await pool.execute(
            "DELETE FROM guild_config WHERE guild_id = $1", interaction.guild_id
        )
        await interaction.response.send_message(
            embed=embeds.warning("Config Reset", "All setup for this server has been wiped."),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Setup(bot))
