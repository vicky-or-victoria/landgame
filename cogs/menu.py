"""
Menu cog.

The public menu embed is visible to everyone in the channel. 
Each button sends an ephemeral follow-up message to ONLY that player with the
sub-menu buttons — so multiple players can interact simultaneously without
interfering with each other.
"""
import discord
from discord.ext import commands
from utils.checks import is_owner
from utils import embeds


# ---------------------------------------------------------------------------
# Ephemeral sub-menu views — sent only to the player who clicks
# ---------------------------------------------------------------------------

class TerritoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Claim Tile", style=discord.ButtonStyle.secondary, custom_id="ep_territory:claim")
    async def claim(self, interaction, button):
        await interaction.response.send_modal(ClaimTileModal())

    @discord.ui.button(label="Develop Tile", style=discord.ButtonStyle.secondary, custom_id="ep_territory:develop")
    async def develop(self, interaction, button):
        await interaction.response.send_modal(DevelopTileModal())

    @discord.ui.button(label="Build", style=discord.ButtonStyle.secondary, custom_id="ep_territory:build")
    async def build(self, interaction, button):
        await interaction.response.send_modal(BuildModal())

    @discord.ui.button(label="Demolish", style=discord.ButtonStyle.secondary, custom_id="ep_territory:demolish")
    async def demolish(self, interaction, button):
        await interaction.response.send_modal(DemolishModal())


class MilitaryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Raise Levy", style=discord.ButtonStyle.secondary, custom_id="ep_military:raise")
    async def raise_levy(self, interaction, button):
        await interaction.response.send_modal(RaiseLevyModal())

    @discord.ui.button(label="Move Army", style=discord.ButtonStyle.secondary, custom_id="ep_military:move")
    async def move(self, interaction, button):
        await interaction.response.send_modal(MoveArmyModal())

    @discord.ui.button(label="Assign to Front", style=discord.ButtonStyle.secondary, custom_id="ep_military:assign")
    async def assign(self, interaction, button):
        await interaction.response.send_modal(AssignFrontModal())

    @discord.ui.button(label="View Armies", style=discord.ButtonStyle.secondary, custom_id="ep_military:view")
    async def view_armies(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.military import get_armies
        armies = await get_armies(interaction.client, interaction.guild_id, interaction.user.id)
        if not armies:
            await interaction.followup.send(embed=embeds.info("Armies", "You have no armies."), ephemeral=True)
            return
        lines = [f"{a['name']} — {a['location']} ({a['size']} troops)" for a in armies]
        await interaction.followup.send(embed=embeds.info("Your Armies", "\n".join(lines)), ephemeral=True)


class EconomyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="View Balance", style=discord.ButtonStyle.secondary, custom_id="ep_economy:balance")
    async def balance(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.players import get_player
        p = await get_player(interaction.client, interaction.guild_id, interaction.user.id)
        if not p:
            await interaction.followup.send(embed=embeds.error("Not Registered", "You are not a registered player."), ephemeral=True)
            return
        await interaction.followup.send(embed=embeds.player_status(p), ephemeral=True)

    @discord.ui.button(label="Collect Tax", style=discord.ButtonStyle.secondary, custom_id="ep_economy:tax")
    async def tax(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.economy import collect_tax
        result = await collect_tax(interaction.client, interaction.guild_id, interaction.user.id)
        await interaction.followup.send(embed=embeds.success("Tax Collected", result), ephemeral=True)

    @discord.ui.button(label="Market", style=discord.ButtonStyle.secondary, custom_id="ep_economy:market")
    async def market(self, interaction, button):
        await interaction.response.send_modal(MarketModal())

    @discord.ui.button(label="Trade", style=discord.ButtonStyle.secondary, custom_id="ep_economy:trade")
    async def trade(self, interaction, button):
        await interaction.response.send_modal(TradeModal())


class PoliticsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Research", style=discord.ButtonStyle.secondary, custom_id="ep_politics:research")
    async def research(self, interaction, button):
        await interaction.response.send_modal(ResearchModal())

    @discord.ui.button(label="Traditions", style=discord.ButtonStyle.secondary, custom_id="ep_politics:traditions")
    async def traditions(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.politics import get_traditions
        t = await get_traditions(interaction.client, interaction.guild_id, interaction.user.id)
        lines = [tr['tradition_id'] for tr in t] if t else ["None unlocked yet."]
        await interaction.followup.send(embed=embeds.politics("Your Traditions", "\n".join(lines)), ephemeral=True)


class DiplomacyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Offer Treaty", style=discord.ButtonStyle.secondary, custom_id="ep_diplomacy:offer")
    async def offer(self, interaction, button):
        await interaction.response.send_modal(TreatyOfferModal())

    @discord.ui.button(label="Declare War", style=discord.ButtonStyle.danger, custom_id="ep_diplomacy:war")
    async def war(self, interaction, button):
        await interaction.response.send_modal(DeclareWarModal())

    @discord.ui.button(label="View Treaties", style=discord.ButtonStyle.secondary, custom_id="ep_diplomacy:view")
    async def view_treaties(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.diplomacy import get_treaties
        treaties = await get_treaties(interaction.client, interaction.guild_id, interaction.user.id)
        if not treaties:
            await interaction.followup.send(embed=embeds.info("Treaties", "No active treaties."), ephemeral=True)
            return
        lines = [f"{t['treaty_type']} with {t['other']} — {t['status']}" for t in treaties]
        await interaction.followup.send(embed=embeds.info("Your Treaties", "\n".join(lines)), ephemeral=True)


class InfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="View Map", style=discord.ButtonStyle.secondary, custom_id="ep_info:map")
    async def view_map(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from renderer.map_renderer import render_map
        img = await render_map(interaction.client, interaction.guild_id)
        await interaction.followup.send(file=img, ephemeral=True)

    @discord.ui.button(label="Inspect Tile", style=discord.ButtonStyle.secondary, custom_id="ep_info:inspect_tile")
    async def inspect_tile(self, interaction, button):
        await interaction.response.send_modal(InspectTileModal())

    @discord.ui.button(label="Leaderboard", style=discord.ButtonStyle.secondary, custom_id="ep_info:leaderboard")
    async def leaderboard(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.players import get_leaderboard
        rows = await get_leaderboard(interaction.client, interaction.guild_id)
        lines = [f"{i+1}. {r['name']} — {r['prestige']} prestige" for i, r in enumerate(rows)]
        await interaction.followup.send(embed=embeds.info("Leaderboard", "\n".join(lines) or "No players yet."), ephemeral=True)


# ---------------------------------------------------------------------------
# Public menu embed + view — visible to everyone, each button opens a
# personal ephemeral sub-menu only that player can see.
# ---------------------------------------------------------------------------

def main_menu_embed() -> discord.Embed:
    e = embeds.info("⚔️ Landgame — Command Center")
    e.description = (
        "Select a category below.\n"
        "Your action menu will appear **only for you** — "
        "multiple players can use the menu at the same time.\n\n"
        "**🗺️ Territory** — claim, develop, and build on tiles\n"
        "**⚔️ Military** — raise and move armies, manage fronts\n"
        "**💰 Economy** — tax, trade, and the market\n"
        "**📜 Politics** — research and traditions\n"
        "**🤝 Diplomacy** — treaties and war\n"
        "**🔍 Info** — map, tile inspection, leaderboard"
    )
    return e


class MainMenuView(discord.ui.View):
    """
    Persistent public view. Each button sends an ephemeral followup with
    the relevant sub-menu — only visible to the player who clicked.
    """

    def __init__(self):
        super().__init__(timeout=None)

    async def _send_ephemeral_submenu(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        view: discord.ui.View
    ):
        """Defer and send an ephemeral message with a sub-menu view."""
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="My Status", style=discord.ButtonStyle.primary, custom_id="main:status", row=0)
    async def status(self, interaction, button):
        await interaction.response.defer(ephemeral=True)
        from db.queries.players import get_player
        p = await get_player(interaction.client, interaction.guild_id, interaction.user.id)
        if not p:
            await interaction.followup.send(
                embed=embeds.error("Not Registered", "You are not registered. Use the registration channel to join."),
                ephemeral=True
            )
            return
        await interaction.followup.send(embed=embeds.player_status(p), ephemeral=True)

    @discord.ui.button(label="🗺️ Territory", style=discord.ButtonStyle.secondary, custom_id="main:territory", row=1)
    async def territory(self, interaction, button):
        e = embeds.info("🗺️ Territory", "Claim, develop, and construct buildings on your tiles.")
        await self._send_ephemeral_submenu(interaction, e, TerritoryView())

    @discord.ui.button(label="⚔️ Military", style=discord.ButtonStyle.secondary, custom_id="main:military", row=1)
    async def military(self, interaction, button):
        e = embeds.info("⚔️ Military", "Raise levies, move armies, and manage frontlines.")
        await self._send_ephemeral_submenu(interaction, e, MilitaryView())

    @discord.ui.button(label="💰 Economy", style=discord.ButtonStyle.secondary, custom_id="main:economy", row=1)
    async def economy(self, interaction, button):
        e = embeds.info("💰 Economy", "Collect taxes, post market orders, and trade with other players.")
        await self._send_ephemeral_submenu(interaction, e, EconomyView())

    @discord.ui.button(label="📜 Politics", style=discord.ButtonStyle.secondary, custom_id="main:politics", row=2)
    async def politics(self, interaction, button):
        e = embeds.politics("📜 Politics", "Unlock research and develop cultural traditions.")
        await self._send_ephemeral_submenu(interaction, e, PoliticsView())

    @discord.ui.button(label="🤝 Diplomacy", style=discord.ButtonStyle.secondary, custom_id="main:diplomacy", row=2)
    async def diplomacy(self, interaction, button):
        e = embeds.info("🤝 Diplomacy", "Offer treaties, declare war, and view your active agreements.")
        await self._send_ephemeral_submenu(interaction, e, DiplomacyView())

    @discord.ui.button(label="🔍 Info", style=discord.ButtonStyle.secondary, custom_id="main:info", row=2)
    async def info(self, interaction, button):
        e = embeds.info("🔍 Info", "View the map, inspect tiles, and check the leaderboard.")
        await self._send_ephemeral_submenu(interaction, e, InfoView())


# ---------------------------------------------------------------------------
# Modals (unchanged logic, but guild_id threaded through handlers)
# ---------------------------------------------------------------------------

class ClaimTileModal(discord.ui.Modal, title="Claim Tile"):
    coord = discord.ui.TextInput(label="Tile Coordinate", placeholder="e.g. A5")
    async def on_submit(self, interaction):
        from cogs.territory import handle_claim
        await handle_claim(interaction, self.coord.value.upper())

class DevelopTileModal(discord.ui.Modal, title="Develop Tile"):
    coord  = discord.ui.TextInput(label="Tile Coordinate", placeholder="e.g. A5")
    amount = discord.ui.TextInput(label="Gold to Invest", placeholder="e.g. 100")
    async def on_submit(self, interaction):
        from cogs.territory import handle_develop
        await handle_develop(interaction, self.coord.value.upper(), int(self.amount.value))

class BuildModal(discord.ui.Modal, title="Build"):
    coord    = discord.ui.TextInput(label="Tile Coordinate", placeholder="e.g. A5")
    building = discord.ui.TextInput(label="Building Name", placeholder="e.g. Barracks")
    async def on_submit(self, interaction):
        from cogs.territory import handle_build
        await handle_build(interaction, self.coord.value.upper(), self.building.value)

class DemolishModal(discord.ui.Modal, title="Demolish Building"):
    coord    = discord.ui.TextInput(label="Tile Coordinate", placeholder="e.g. A5")
    building = discord.ui.TextInput(label="Building Name", placeholder="e.g. Barracks")
    async def on_submit(self, interaction):
        from cogs.territory import handle_demolish
        await handle_demolish(interaction, self.coord.value.upper(), self.building.value)

class RaiseLevyModal(discord.ui.Modal, title="Raise Levy"):
    coord = discord.ui.TextInput(label="Tile Coordinate", placeholder="e.g. A5")
    async def on_submit(self, interaction):
        from cogs.military import handle_raise_levy
        await handle_raise_levy(interaction, self.coord.value.upper())

class MoveArmyModal(discord.ui.Modal, title="Move Army"):
    army_id = discord.ui.TextInput(label="Army ID", placeholder="e.g. 3")
    coord   = discord.ui.TextInput(label="Destination Tile", placeholder="e.g. B6")
    async def on_submit(self, interaction):
        from cogs.military import handle_move_army
        await handle_move_army(interaction, int(self.army_id.value), self.coord.value.upper())

class AssignFrontModal(discord.ui.Modal, title="Assign to Front"):
    army_id = discord.ui.TextInput(label="Army ID", placeholder="e.g. 3")
    coord   = discord.ui.TextInput(label="Frontline Tile", placeholder="e.g. C7")
    async def on_submit(self, interaction):
        from cogs.military import handle_assign_front
        await handle_assign_front(interaction, int(self.army_id.value), self.coord.value.upper())

class MarketModal(discord.ui.Modal, title="Market Order"):
    resource   = discord.ui.TextInput(label="Resource", placeholder="gold / food / materials")
    amount     = discord.ui.TextInput(label="Amount", placeholder="e.g. 100")
    price      = discord.ui.TextInput(label="Price per Unit", placeholder="e.g. 5")
    order_type = discord.ui.TextInput(label="Order Type", placeholder="buy / sell")
    async def on_submit(self, interaction):
        from cogs.economy import handle_market_order
        await handle_market_order(interaction, self.resource.value, int(self.amount.value), int(self.price.value), self.order_type.value)

class TradeModal(discord.ui.Modal, title="Trade with Player"):
    target   = discord.ui.TextInput(label="Player Name", placeholder="e.g. PlayerName")
    resource = discord.ui.TextInput(label="Resource", placeholder="gold / food / materials")
    amount   = discord.ui.TextInput(label="Amount", placeholder="e.g. 100")
    async def on_submit(self, interaction):
        from cogs.economy import handle_trade
        await handle_trade(interaction, self.target.value, self.resource.value, int(self.amount.value))

class ResearchModal(discord.ui.Modal, title="Research"):
    research_id = discord.ui.TextInput(label="Research ID", placeholder="e.g. advanced_farming")
    async def on_submit(self, interaction):
        from cogs.politics import handle_research
        await handle_research(interaction, self.research_id.value)

class TreatyOfferModal(discord.ui.Modal, title="Offer Treaty"):
    target      = discord.ui.TextInput(label="Player Name", placeholder="e.g. PlayerName")
    treaty_type = discord.ui.TextInput(label="Treaty Type", placeholder="alliance / nap / trade")
    async def on_submit(self, interaction):
        from cogs.diplomacy import handle_offer_treaty
        await handle_offer_treaty(interaction, self.target.value, self.treaty_type.value)

class DeclareWarModal(discord.ui.Modal, title="Declare War"):
    target = discord.ui.TextInput(label="Player Name", placeholder="e.g. PlayerName")
    async def on_submit(self, interaction):
        from cogs.diplomacy import handle_declare_war
        await handle_declare_war(interaction, self.target.value)

class InspectTileModal(discord.ui.Modal, title="Inspect Tile"):
    coord = discord.ui.TextInput(label="Tile Coordinate", placeholder="e.g. A5")
    async def on_submit(self, interaction):
        from cogs.info import handle_inspect_tile
        await handle_inspect_tile(interaction, self.coord.value.upper())


# ---------------------------------------------------------------------------
# Cog
# ---------------------------------------------------------------------------

class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Register persistent views so buttons survive bot restarts
        bot.add_view(MainMenuView())

    @discord.app_commands.command(name="deploy_menu", description="Post the persistent menu to the configured menu channel")
    @is_owner()
    async def deploy_menu(self, interaction: discord.Interaction):
        cfg = self.bot.guild_config(interaction.guild_id)
        channel_id = await cfg.get_channel("menu")
        if not channel_id:
            await interaction.response.send_message(
                embed=embeds.error("Menu channel not set.", "Use /setup_channel menu #channel first."),
                ephemeral=True
            )
            return
        channel = self.bot.get_channel(channel_id)
        msg = await channel.send(embed=main_menu_embed(), view=MainMenuView())
        await cfg.set_menu_message(msg.id)
        await interaction.response.send_message(embed=embeds.success("Menu deployed."), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Menu(bot))
