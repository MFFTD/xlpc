import discord
import botconfig
from discord.ext import commands

# This class is for syncing the bots slash commands to Discord
class Sync(commands.Cog):
    # Usage
    # Type $sync to any of the discord text channels
    # 
    # Do not use when not needed
    # This uses alot of api calls and can lock you out of development fast
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="sync")
    @commands.has_permissions(administrator=True)
    async def sync_commands(self, ctx):
        await self.bot.tree.sync(guild=discord.Object(id=botconfig.guild_id))

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Sync(bot),
        guilds= [discord.Object(id = botconfig.guild_id)])