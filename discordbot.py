import discord
from discord.ext import commands, tasks
import os
from datetime import datetime, time, timedelta


# Get the API token from the .env file.
TOKEN = os.getenv("TOKEN")
SERVER = os.getenv("SERVER")
CHANNEL = int(os.getenv("CHANNEL"))  # Add the channel ID to your .env file

if TOKEN is None:
    raise ValueError("No TOKEN found in environment variables")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == SERVER:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    send_message.start()

@tasks.loop(seconds=3)
async def send_message():
    channel = client.get_channel(CHANNEL)
    if channel:
        await channel.send("whoopywhoop")
        await client.close()  # Exit after sending the message

client.run(TOKEN)

