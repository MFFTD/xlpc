import asyncio
import discord
import botconfig
import aiosqlite
from discord.ext import commands
from utils.db import AsyncSQLiteDB
from cogs.fight import ChallengeView
from cogs.fight import PostANewChallengeView
from utils.challenge_utils import fetch_challenge_message_data

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='$', intents=discord.Intents.all(), application_id=botconfig.application_id)
        self.initial_extensions = [
            'cogs.sync',
            'cogs.register',
            'cogs.invite',
            'cogs.fight'
        ]

    async def setup_hook(self) -> None:
        # Initial extensions (cogs) that the bot will load
        # Cogs are a way to organize commands, listeners, and other functionality into separate modules
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        
        # Fetching message data of the posted challenges messages because the buttons are persistent and we need to load persistent views between bot restarts
        message_data = await fetch_challenge_message_data()
        if message_data:
            for data in message_data:
                message_id = data["message_id"]
                author = data["author"]
                team_name = data["team_name"]
                # These are the persistent views
                # They are the the buttons to accept a challenge
                self.add_view(ChallengeView(message_id=message_id, author=author, team_name=team_name), message_id=message_id)

        # This view is a persistent view
        # Button that triggers the modal to post a new challenge
        self.add_view(PostANewChallengeView(), message_id=botconfig.persistent_challenge_button_message_id)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

async def main() -> None:
    bot = MyBot()
    try:
        await bot.start(botconfig.token)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await bot.close()

if __name__ == '__main__':
    asyncio.run(main())
