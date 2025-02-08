import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from datetime import datetime, time, timedelta

load_dotenv()

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

@tasks.loop(hours=24)
async def send_message():
    now = datetime.utcnow()
    target_time = datetime.combine(now.date(), time(8, 0))  # 8 AM UTC
    if now > target_time:
        target_time += timedelta(days=1)
    await discord.utils.sleep_until(target_time)

    channel = client.get_channel(CHANNEL)
    if channel:
        await channel.send("Hello, world!")

client.run(TOKEN)