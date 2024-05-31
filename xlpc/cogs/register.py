import asyncio
import discord
import botconfig
from discord.ext import commands
from discord import app_commands
from utils.db import AsyncSQLiteDB
from utils.team_utils import check_if_team_leader

# This class is used to handle register-related commands and interactions
class Register(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @app_commands.command(name="register_team", description="Register a new team")
    async def register(self, interaction: discord.Interaction, team_name: str):
        # Getting the Discord guild roles
        # To check if there already is a role with the team name that is being registered here
        guild_roles = await interaction.guild.fetch_roles()
        role_exists = any(role.name == team_name for role in guild_roles)

        if role_exists:
            await interaction.response.send_message(f"Team with the name `{team_name}` already exists.")
            return

        try:
            team_name = await check_if_team_leader(interaction.user.id)
        except Exception as e:
            print(f"Error in invite(Checking if user is a team leader): {e}")
        
        if team_name:
            await interaction.response.send_message(f"You are already the leader of the team {team_name}.\nYou can only be the leader of one team.", ephemeral=True)
            return            
        
        try:
            insert_a_new_team_query = "INSERT INTO team (team_name, team_leader) VALUES (?, ?)"
            params = (team_name, interaction.user.id)
            await self.db.execute_query(insert_a_new_team_query, params)
        except Exception as e:
            print(f"Error registering a new team: {e}")
            return

        register_embed = discord.Embed(
            title=("New team registered"),
            description=(f"Team name: `{team_name}`\nLeader: {interaction.user.mention}"),
            color=0x00000
        )

        # Create a new Discord role for the team and give it to the interaction user
        new_team_role = await interaction.guild.create_role(name=team_name, hoist=True)
        await interaction.user.add_roles(new_team_role)
        await interaction.response.send_message(embed=register_embed)

# This function is to add this cog to the bot       
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Register(bot),
        guilds= [discord.Object(id = botconfig.guild_id)])
