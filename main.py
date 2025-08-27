import discord
from discord.ext import commands
import os
import dotenv

dotenv.load_dotenv()

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True  # ✅ allows bot to read message text
bot = commands.Bot(command_prefix="!", intents=intents)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Command: Respond to a message
@bot.command()
async def hello(ctx):
    await ctx.send("Hello! 👋")

@bot.event
async def on_message(message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Respond to "hi" (works in servers and DMs)
    await message.reply(f"Hello!, you said {message.content}", mention_author=False)

    # Allow commands to still work
    await bot.process_commands(message)

# Run the bot
token = os.getenv('BOT_TOKEN')
bot.run(token)
