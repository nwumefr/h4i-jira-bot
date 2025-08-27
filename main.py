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

# function to get the ticket pile
@bot.command()
@commands.has_role("Admin")
async def pile(ctx, limit:int=10):
    await ctx.send("Here is the pile of the last ")
    # attempt to load ticket pile
    url = "http://localhost:5000/pile"  
    logger.info('trying to push ticket')
    async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print("Status:", response.status)
                data = await response.json()
                print(data)
                print("Response:", data)
                lim = limit
                for i in data['tickets']:
                    if lim>0:
                        ticket_data = i
                        # ticket data has the same schema as Ticket
                        embed = discord.Embed(
                            title=f"Ticket ID #{ticket_data['id']}",
                            description=f"content: {ticket_data['content']}",
                            color=discord.Color.blurple()  # you can use any color
                        )
                        embed.add_field(name="Issuer", value=f"{ticket_data['issuer']}", inline=False)
                        embed.add_field(name="Assigned To", value=f"{ticket_data['assigned_to']}", inline=True)
                        embed.add_field(name="Status", value=f"{ticket_data['status']}", inline=True)
                        embed.set_footer(text="Bot is still in beta")
            
                        await ctx.send(embed=embed)
                        lim-=1
                    else:
                        break

# command to assign ticket to someone
@bot.command()
@commands.has_role("Admin")
async def assigne(ctx, assigned_to):
    pass

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Only respond to messages in guilds (not DMs)
    if message.guild is None:
        return
    
    # Check if bot is mentioned
    if bot.user in message.mentions:
        # build ticket
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
            f"Hello!, your ticket has been put in:{message.content}", 
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
