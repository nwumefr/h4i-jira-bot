import discord
from discord.ext import commands
import os
import dotenv
from utils.ticket import Ticket
from uuid import uuid4, UUID

dotenv.load_dotenv()

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True  # ✅ allows bot to read message text
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# function to build tickets

@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Respond to "hi" (works in servers and DMs)
    new_ticket = Ticket(
        id=str(uuid4()),
        issuer=str(message.author),
        content=str(message.content),)

    embed = discord.Embed(
        title=f"Ticket ID #{new_ticket.id}",
        description=f"content: {new_ticket.content}",
        color=discord.Color.blurple()  # you can use any color
    )
    
    embed.add_field(name="Issuer", value=f"{new_ticket.issuer}", inline=False)
    embed.add_field(name="Assigned To", value="None", inline=True)
    embed.set_footer(text="Bot is still in beta")
    
    await message.reply(
        f"Hello!, you said {message.content}", 
        mention_author=False,
        embed=embed)

    # Allow commands to still work
    await bot.process_commands(message)

# Run the bot
token = os.getenv('BOT_TOKEN')
bot.run(token)
