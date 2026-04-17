"""
Registration cog — posts a persistent embed with a Register button.
Clicking grants the configured player role and registers the user in the DB.
The embed live-updates its registered player counter.
"""
import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import is_owner
from utils import embeds
from db.queries.players import register_player, count_players, get_player


def make_registration_embed(player_count: int) -> discord.Embed:
    e = embeds.info(
        "⚔️ Join the Game",
        f"Click **Register** below to join Landgame.\n\n"
        f"You will receive the player role and start with starter resources.\n\n"
        f"👥 **Registered players: {player_count}**"
    )
    return e


class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Register",
        style=discord.ButtonStyle.success,
        custom_id="registration:register",
        emoji="⚔️"
    )
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        guild_id = interaction.guild_id
        discord_id = interaction.user.id

        # Check if already registered
        existing = await get_player(interaction.client, guild_id, discord_id)
        if existing:
            await interaction.followup.send(
                embed=embeds.error("Already Registered", "You are already registered in this server."),
                ephemeral=True
            )
            return

        # Register in DB
        name = interaction.user.display_name
        await register_player(interaction.client, guild_id, discord_id, name)

        # Grant player role if configured
        cfg = interaction.client.guild_config(guild_id)
        player_role_id = await cfg.get_player_role()
        role_mention = ""
        if player_role_id:
            role = interaction.guild.get_role(player_role_id)
            if role:
                try:
                    await interaction.user.add_roles(role, reason="Landgame registration")
                    role_mention = f"\nYou have been given the {role.mention} role."
                except discord.Forbidden:
                    role_mention = "\n⚠️ Could not assign role — check bot permissions."

        # Update registration embed counter
        reg_msg_data = await cfg.get_registration_message()
        if reg_msg_data:
            try:
                channel = interaction.client.get_channel(reg_msg_data["channel_id"])
                if channel:
                    msg = await channel.fetch_message(reg_msg_data["message_id"])
                    new_count = await count_players(guild_id)
                    await msg.edit(embed=make_registration_embed(new_count))
            except Exception:
                pass  # Non-fatal — counter update best-effort

        await interaction.followup.send(
            embed=embeds.success(
                "Welcome!",
                f"You are now registered as **{name}**.{role_mention}\n\n"
                "Use `/menu` or the menu channel to start playing."
            ),
            ephemeral=True
        )


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.add_view(RegisterView())

    @app_commands.command(
        name="deploy_registration",
        description="Post the registration embed with Register button to a channel"
    )
    @is_owner()
    async def deploy_registration(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        guild_id = interaction.guild_id
        cfg = self.bot.guild_config(guild_id)

        current_count = await count_players(guild_id)
        msg = await channel.send(
            embed=make_registration_embed(current_count),
            view=RegisterView()
        )

        player_role_id = await cfg.get_player_role()
        await cfg.set_registration_message(channel.id, msg.id, player_role_id)

        await interaction.response.send_message(
            embed=embeds.success(
                "Registration Deployed",
                f"Registration embed posted in {channel.mention}."
            ),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Registration(bot))
