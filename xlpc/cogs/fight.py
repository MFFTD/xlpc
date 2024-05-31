import discord
import channels
import botconfig
import traceback
from discord.utils import get
from discord.ext import commands
from discord import app_commands
from utils.team_utils import check_if_team_leader
from discord.app_commands import checks, MissingPermissions
from utils.challenge_utils import insert_challenge_message_data_to_db

# Modal class to ask user input information about a new challenge they want to post
class ChallengeModal(discord.ui.Modal, title='Post a new challenge'):
    def __init__(self, author, team_name):
        super().__init__()
        self.author = author
        self.team_name = team_name

    opts = discord.ui.TextInput(
        label='Opts',
        style=discord.TextStyle.short,
        placeholder='How big of a fight are you looking for?',
        required=True
    )

    info = discord.ui.TextInput(
        label='Additional rules or info?',
        style=discord.TextStyle.long,
        placeholder='[OPTIONAL] For example binds only / date and time',
        required=False,
        max_length=300,
    )

    # This method executes when user submits the form(modal)
    async def on_submit(self, interaction: discord.Interaction):
        # Fetching discord channel
        # So we can then send messages to it later
        challenge_channel = interaction.guild.get_channel(channels.challenge_channel_id)
        if not challenge_channel:
            print(f"#challenges-channel not found with the channel id: {channels.challenge_id}")

        # Embedded messages are rich, styled messages that can contain fields, images, and more 
        # They are commonly used for sending detailed information in a visually appealing format.
        challenge_embed = discord.Embed(
            title=f"New challenge posted by team [{self.team_name}]",
            description=f"Opts: {self.opts}\n\nAdditional info / rules:\n{self.info}",
            color=0x00000
        )

        # We need to send an embed and a button
        #
        # Sending embed only first so we can get the message object
        # And with having the message object we can pass it to ChallengeView class
        message = await challenge_channel.send(embed=challenge_embed)
        # From the object we want the message.id
        # With the message.id we can dynamically construct a new button with unique custom_id for every challenge being posted(meaning every button will be unique)
        # This way we can distinct which button is being clicked
        accept_challenge_view = ChallengeView(message.id, self.author, self.team_name)
        # Now that the unique button is constructed in the ChallengeView, initialize so we can use the button
        # Edit the message that first just sent the embed, edit it to add the button
        await message.edit(embed=challenge_embed, view=accept_challenge_view)
        """
        This is a note what needs to be implemented
        # Create new unique button to cancel the fight
        # Send the button with the interaction response message
        # Get the interaction object and pass the id as an ato ChallengeView
        # Get the interaction object (message = await interaction.original_response())and initialize ChallengeView class and pass the id as an argument
        # In button callback DELETE the MESSAGE THAT HAS THE delete fight button 
        # Vice versa DELETE the CHALLENGE embed and button IF delete fight button gets pressed
        # Lastly delete the message data from db if challenge is accepted or deleted by the author
        """
        # Here we would want to send a persistent decline button so the author could cancel the post
        await interaction.response.send_message("Challenge posted successfully!", ephemeral=True)
        # Saving this data to database, we want to have them cause need to fetch them on bot restart
        # The persistent views needs the message ids and those other values are what we are going to use in the views
        await insert_challenge_message_data_to_db(message.id, self.author, self.team_name)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.followup.send('Oops! Something went wrong.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)

# This class is to handle the creation and management 
# Of persistent view (button) that allows users to accept a challenge
#
# Decline button needs to be implemented
class ChallengeView(discord.ui.View):
    def __init__(self, message_id, author, team_name):
        super().__init__(timeout=None)
        self.message_id = message_id
        self.author = author
        self.team_name = team_name
        # Defining buttons in the class constructor
        # So we can manually set an unique custom_id for each button
        self.accept_button = discord.ui.Button(
            label="Accept the challenge",
            custom_id=f"accept_challenge_{self.message_id}",
            style=discord.ButtonStyle.green
        )
        # Assigns the callback method accept_challenge_button_callback to be called when the button is clicked
        self.accept_button.callback = self.accept_challenge_button_callback
        # Adds the accept_button to the view, making it part of the interactive UI components that will be displayed.
        self.add_item(self.accept_button)
        
    async def accept_challenge_button_callback(self, interaction: discord.Interaction):
        team_role = get(interaction.guild.roles, name=self.team_name)
        # checking that user who clicks button is not the one who posted the fight
        # and checking if the teams role still exists and that the user accepting
        # is not in the same team than the one who created the challenge
        if interaction.user.id == self.author or (team_role and team_role in interaction.user.roles):
            await interaction.response.send_message("You can not accept your own team's challenge.", ephemeral=True)
            return

        self.accept_button.disabled = True
        await interaction.response.edit_message(view=self)

# This class holds the button that is clicked when you want to create a new challenge
# The button is only ever being sent once, it will be on its own Discord text channel and it will persists ther
# The button can be sent with a slash command /send_persistent_fight_views
class PostANewChallengeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Post a new fight", custom_id="fight_button", style=discord.ButtonStyle.green)
    async def challenge_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Checking if the interaction.user is a team leader
            team_name = await check_if_team_leader(interaction.user.id)
            if not team_name:
                await interaction.response.send_message("You are not a team leader.", ephemeral=True)
                return
        except Exception as e:
            print(f"Error checking if team leader: {e}")
            return

        # When button is pressed, trigger the modal that is used to post a new challenge
        await interaction.response.send_modal(ChallengeModal(interaction.user.id, team_name))

# This class is used to handle fight-related commands and interactions
class Fight(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="send_persistent_fight_views", description="Sends the create fight embed and button")
    @checks.has_permissions(administrator=True)
    async def send_challenge_button(self, interaction: discord.Interaction):
        view = PostANewChallengeView()
        await interaction.response.send_message(content="test", view=view)
        message = await interaction.original_response()

# This function is to add this cog to the bot
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        Fight(bot),
        guilds=[discord.Object(id=botconfig.guild_id)])
