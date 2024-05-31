import asyncio
import discord
import botconfig
from discord.utils import get
from discord.ext import commands
from discord import app_commands
from utils.db import AsyncSQLiteDB
from utils.team_utils import check_if_team_leader

# This class holds buttons to accept and decline invitations to a team
class Confirm(discord.ui.View):
    def __init__(self, team_name, user_being_invited, invite_embed):
        super().__init__(timeout=300.0)
        self.value = None
        self.team_name = team_name
        self.invite_embed = invite_embed
        self.user_being_invited = user_being_invited
    
    # This is executed when the buttons are 300 seconds old and disables the buttons
    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
            
            self.invite_embed.title = "Invite (Timed Out)"

        if self.message:
            await self.message.edit(embed=self.invite_embed, view=self)

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user_being_invited:
            return
        team_role = get(interaction.guild.roles, name=f"{self.team_name}")

        self.stop()
        self.value = True
        # the children are the buttons. children of the view class
        self.children[0].disabled = True
        self.children[1].disabled = True
        # This needs to be called to actually disable the buttons
        await interaction.response.edit_message(view=self)
        # Give the user being invited the Teams role(discord role)
        await interaction.user.add_roles(team_role)
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.invited_user_id:
            return
        
        self.stop()
        self.value = False
        self.children[1].disabled = True
        self.children[0].disabled = True

        await interaction.response.edit_message(view=self)  

# This class is used to handle invite-related commands and interactions
class Invite(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = AsyncSQLiteDB(botconfig.db_path)

    # Slash command
    # Can be used in discord with typing /invite
    @app_commands.command(name="invite", description="Invite users to your team")
    async def invite_to_team(self, interaction: discord.Interaction, user: discord.Member):
        
        if user == interaction.user:
            await interaction.response.send_message("You should not invite yourself. Ask a team leader to invite you incase you wish to join a team.", ephemeral=True)
            return

        try:
            result = await check_if_team_leader(self.db, interaction.user.id)
            team_name = result[0][1] # This should probably be done at the check_if_team_leader function
        except Exception as e:
            print(f"Error in invite(Checking if user is a team leader): {e}")
        
        if not result:
            await interaction.response.send_message("You are not a team leader.")
            return
        
        # Embedded messages are rich, styled messages that can contain fields, images, and more 
        # They are commonly used for sending detailed information in a visually appealing format.
        invite_embed = discord.Embed(
            title="Invite",
            description=f"Inviting user: {user.mention}\nTo: `{team_name}`\nBy: {interaction.user.mention}",
            color=0x00000
        )

        view = Confirm(team_name, user, invite_embed)

        await interaction.response.send_message(embed=invite_embed, view=view)
        # Get the interaction response so it can be edited later
        # In this case we want it to disable the view on timeout
        view.message = await interaction.original_response()

# This function is to add this cog to the bot
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Invite(bot),
        guilds=[discord.Object(id = botconfig.guild_id)])