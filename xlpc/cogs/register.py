import asyncio
import discord
import botconfig
from discord.ext import commands
from discord import app_commands
from utils.db import AsyncSQLiteDB

# This class is used to handle register-related commands and interactions
class Register(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = AsyncSQLiteDB(botconfig.db_path)
    
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
            check_if_team_leader_query = "SELECT team_leader, team_name FROM team WHERE team_leader = ?"
            params = (interaction.user.id,)
            result = await self.db.execute_query(check_if_team_leader_query, params, fetchall=True)
        except Exception as e:
            await interaction.response.send_message("Error registering a team", ephemeral=True)
            print(f"Error inviting user to the team: {e}")
            return
        
        if result:
            print("You are already a leader of a team, you can be only leader of 1 team.", ephemeral=True)
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