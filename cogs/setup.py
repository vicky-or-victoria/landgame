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

    @app_commands.command(name="setup_channel", description="Assign a bot channel")
    @is_owner()
    async def setup_channel(self, interaction: discord.Interaction, channel_type: str, channel: discord.TextChannel):
        if channel_type not in CHANNEL_NAMES:
            await interaction.response.send_message(
                embed=embeds.error("Invalid channel type", f"Valid types: {', '.join(CHANNEL_NAMES)}"),
                ephemeral=True
            )
            return
        self.bot.config.set_channel(channel_type, channel.id)
        missing = self.bot.config.get_missing_channels()
        if not missing and self.bot.config.get_gm_role():
            self.bot.config.mark_setup_complete()
        await interaction.response.send_message(
            embed=embeds.success("Channel Set", f"{channel_type} → {channel.mention}"),
            ephemeral=True
        )

    @app_commands.command(name="setup_gmrole", description="Assign the GM role")
    @is_owner()
    async def setup_gmrole(self, interaction: discord.Interaction, role: discord.Role):
        self.bot.config.set_gm_role(role.id)
        missing = self.bot.config.get_missing_channels()
        if not missing:
            self.bot.config.mark_setup_complete()
        await interaction.response.send_message(
            embed=embeds.success("GM Role Set", f"{role.mention} is now the GM role"),
            ephemeral=True
        )

    @app_commands.command(name="setup_status", description="Check setup progress")
    @is_owner()
    async def setup_status(self, interaction: discord.Interaction):
        missing = self.bot.config.get_missing_channels()
        gm_role = self.bot.config.get_gm_role()
        lines = []
        for name in CHANNEL_NAMES:
            val = self.bot.config.get_channel(name)
            lines.append(f"{name}: {'set' if val else 'missing'}")
        lines.append(f"gm_role: {'set' if gm_role else 'missing'}")
        lines.append(f"setup_complete: {self.bot.config.is_setup_complete()}")
        await interaction.response.send_message(
            embed=embeds.info("Setup Status", "\n".join(lines)),
            ephemeral=True
        )

    @app_commands.command(name="setup_reset", description="Wipe all config and start fresh")
    @is_owner()
    async def setup_reset(self, interaction: discord.Interaction):
        import json
        from utils.config_manager import DEFAULT, CONFIG_PATH
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT, f, indent=4)
        self.bot.config.data = DEFAULT.copy()
        await interaction.response.send_message(
            embed=embeds.warning("Config Reset", "All setup has been wiped."),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Setup(bot))
