import discord
from discord.ext import commands
import os
import dotenv
from utils.pydantic_models import Ticket, TicketRequest
from uuid import uuid4, UUID
import aiohttp
import asyncio
import logging
import datetime
import json
dotenv.load_dotenv()

# logging
logger = logging.getLogger('main-logger')

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
        content=str(message.content),
        date_started=str(datetime.datetime.now()))

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
    
    # attempt to send ticket to engine microservice
    url = "http://localhost:5000/push"  
    payload = new_ticket.model_dump()
    logger.info('trying to push ticket')
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            print("Status:", response.status)
            data = await response.json()
            print("Response:", data)
    # Allow commands to still work
    await bot.process_commands(message)

# Run the bot
token = os.getenv('BOT_TOKEN')
bot.run(token)
